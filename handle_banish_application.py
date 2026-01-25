from typing import List

from nonebot.adapters.onebot.v11 import GroupMessageEvent, GROUP_ADMIN, GROUP_OWNER, Message, Bot
from nonebot.internal.params import Depends
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin.on import on_command

from ys_bot.plugins.nonebot_plugin_management.data_handle.blacklist_information_util import BlacklistInformation
from ys_bot.plugins.nonebot_plugin_management.data_handle.intendant_information_util import INTENDANT
from ys_bot.plugins.nonebot_plugin_management.msg_util import get_msg_at

kick = on_command('踢', aliases={"t", "踢出", "kick","飞机","飞机票"}, priority=5, block=True,
                  permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER | INTENDANT)

# 新增命令：查看黑名单
view_blacklist = on_command('查看黑名单', aliases={"黑名单", "blacklist", "查看黑名单列表"}, priority=5, block=True,
                            permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER | INTENDANT)

# 新增命令：移出黑名单
remove_blacklist = on_command('移出黑名单', aliases={"移除黑名单", "unblacklist", "移除黑名单成员"}, priority=5, block=True,
                              permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER | INTENDANT)

# 新增命令：清空黑名单
clear_blacklist = on_command('清空黑名单', aliases={"清空黑名单列表", "clearblacklist"}, priority=5, block=True,
                             permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)

@kick.handle()
async def handle_kick_application(bot: Bot, event: GroupMessageEvent,
                                  user: List = Depends(get_msg_at)):
    group_id = event.group_id
    blacklist_util = BlacklistInformation(group_id)
    if not user:
        await bot.send(event, "请@需要踢出的群员")
        return

    try:
        # 获取群成员列表来检查用户是否在群中
        member_list = await bot.get_group_member_list(group_id=group_id)
        member_ids = {str(member['user_id']) for member in member_list}

        for u in user:
            user_id = str(u)
            if user_id not in member_ids:
                await bot.send(event, f"用户 {user_id} 不在本群，已添加至黑名单")
                blacklist_util.add_to_blacklist(user_id=u)
                continue

            try:
                # 获取用户信息以检查是否是管理员/群主
                member_info = await bot.get_group_member_info(group_id=group_id, user_id=u)

                # 检查用户权限（0普通成员，1管理员，2群主）
                if member_info.get('role') in ['admin', 'owner']:
                    await bot.send(event, f"无法踢出群管理或群主: {user_id}")
                    continue
                # blacklist_util.add_to_blacklist(user_id=u)
                # 将添加黑名单操作放如 on_notice
                # 原因：notice方面通过黑名单判断逻辑
                await bot.set_group_kick(group_id=group_id, user_id=u, reject_add_request=True)
                await bot.send(event, f"已踢出用户: {user_id}，拒绝后续申请并加入黑名单")

            except Exception as e:
                # 更具体的错误处理
                error_msg = str(e)
                if "group admin" in error_msg or "group owner" in error_msg:
                    await bot.send(event, f"无法踢出群管理或群主: {user_id}")
                else:
                    await bot.send(event, f"踢出用户 {user_id} 时出错: {error_msg}")

    except Exception as e:
        await bot.send(event, f"操作失败: {str(e)}")

@view_blacklist.handle()
async def handle_view_blacklist(bot: Bot, event: GroupMessageEvent):
    """查看当前群组的黑名单列表"""
    group_id = event.group_id
    blacklist_util = BlacklistInformation(group_id)

    try:
        blacklist = blacklist_util.get_blacklist()

        if not blacklist:
            await bot.send(event, "当前群组的黑名单为空。")
            return

        # 格式化显示黑名单列表
        blacklist_count = len(blacklist)
        blacklist_text = "\n".join([f"{i+1}. {user_id}" for i, user_id in enumerate(blacklist)])

        message = f"当前群组黑名单列表 (共{blacklist_count}人):\n{blacklist_text}"
        await bot.send(event, message)

    except Exception as e:
        await bot.send(event, f"获取黑名单失败: {str(e)}")

@remove_blacklist.handle()
async def handle_remove_blacklist(bot: Bot, event: GroupMessageEvent,
                                  msg: Message = CommandArg()):
    """将用户从黑名单中移除，支持QQ号参数"""
    group_id = event.group_id
    blacklist_util = BlacklistInformation(group_id)

    # 获取消息文本
    msg_text = msg.extract_plain_text().strip()

    if not msg_text:
        await bot.send(event, "请输入要移出黑名单的QQ号，格式：/移出黑名单 QQ号")
        return

    try:
        # 解析QQ号（支持多个QQ号，用空格或逗号分隔）
        qq_numbers = []
        for part in msg_text.replace(',', ' ').split():
            if part.strip():
                qq_numbers.append(part.strip())

        if not qq_numbers:
            await bot.send(event, "未检测到有效的QQ号，请检查输入格式")
            return

        success_count = 0
        failed_count = 0

        for qq_str in qq_numbers:
            # 验证QQ号格式
            if not qq_str.isdigit():
                await bot.send(event, f"QQ号格式错误：{qq_str}，必须是纯数字")
                failed_count += 1
                continue

            user_id = str(qq_str)

            # 检查用户是否在黑名单中并移除
            if blacklist_util.remove_from_blacklist(user_id):
                success_count += 1
            else:
                await bot.send(event, f"用户 {user_id} 不在黑名单中")
                failed_count += 1

        # 发送结果总结
        result_message = f"移出黑名单操作完成：\n"
        result_message += f"✓ 成功移出：{success_count} 位用户\n"

        if failed_count > 0:
            result_message += f"✗ 失败：{failed_count} 位用户（不在黑名单中或格式错误）"

        await bot.send(event, result_message)

    except Exception as e:
        await bot.send(event, f"移出黑名单失败: {str(e)}")


@clear_blacklist.handle()
async def handle_clear_blacklist(bot: Bot, event: GroupMessageEvent):
    """清空当前群组的黑名单"""
    group_id = event.group_id
    blacklist_util = BlacklistInformation(group_id)

    try:
        # 获取当前黑名单数量
        current_blacklist = blacklist_util.get_blacklist()
        blacklist_count = len(current_blacklist)

        if blacklist_count == 0:
            await bot.send(event, "当前群组的黑名单已为空。")
            return

        # 清空黑名单
        if blacklist_util.clear_blacklist():
            await bot.send(event, f"已清空黑名单，共移除 {blacklist_count} 位用户")
        else:
            await bot.send(event, "清空黑名单失败")

    except Exception as e:
        await bot.send(event, f"清空黑名单失败: {str(e)}")