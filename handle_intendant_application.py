# handle_intendant_application.py 的完整代码
from typing import List

from nonebot.adapters.onebot.v11 import Bot, GROUP_ADMIN, GROUP_OWNER, GroupMessageEvent
from nonebot.internal.params import Depends
from nonebot.permission import SUPERUSER
from nonebot.plugin.on import on_command

from ys_bot.plugins.nonebot_plugin_management.data_handle.intendant_information_util import IntendantInformation
from ys_bot.plugins.nonebot_plugin_management.msg_util import get_msg_at

add_intendant = on_command('添加管理员', aliases={"添加管理", "添加管", "intendant", "addintendant", "add_intendant"},
                           permission=SUPERUSER | GROUP_OWNER, block=True, priority=5)


@add_intendant.handle()
async def handle_intended_application(
        bot: Bot, event: GroupMessageEvent, user: List = Depends(get_msg_at)):
    if user is None or len(user) == 0:
        await bot.send(event, "请@需要添加为管理员的用户")
        return
    group_id = event.group_id
    intendant_util = IntendantInformation(group_id)
    for u in user:
        if intendant_util.is_intendant(u):
            await bot.send(event, f"{u}已经是管理员了")
        else:
            intendant_util.add_intendant(u)
            await bot.send(event, f"成功添加管理员{u}")
    return


delete_intendant = on_command('删除管理员',
                              aliases={"减少管理", "删除管理", "减少管理员", "del_intendant", "delete_intendant",
                                       "deleteintendant", "delintendant"},
                              block=True,
                              permission=SUPERUSER | GROUP_OWNER, priority=5)


@delete_intendant.handle()
async def handle_delete_intendant(bot: Bot, event: GroupMessageEvent, user: List = Depends(get_msg_at)):
    if user is None or len(user) == 0:
        await bot.send(event, "请@需要删除的管理员用户")
        return

    group_id = event.group_id
    intendant_util = IntendantInformation(group_id)

    for u in user:
        if intendant_util.is_intendant(u):
            intendant_util.remove_intendant(u)
            await bot.send(event, f"成功删除管理员{u}")
        else:
            await bot.send(event, f"{u}不是管理员")
    return


list_intendant = on_command('查询管理员',
                            aliases={"查看管理员", "管理员列表", "list_intendant", "listintendant", "showintendant"},
                            block=True,
                            permission=SUPERUSER | GROUP_OWNER | GROUP_ADMIN, priority=5)


@list_intendant.handle()
async def handle_list_intendant(bot: Bot, event: GroupMessageEvent):
    group_id = event.group_id
    intendant_util = IntendantInformation(group_id)

    intendants = intendant_util.get_intendants()

    if not intendants:
        await bot.send(event, "当前群组暂无管理员")
        return

    # 格式化输出管理员列表
    intendants_list = "\n".join([f"{i + 1}. {uid}" for i, uid in enumerate(intendants)])
    await bot.send(event, f"当前群组管理员列表：\n{intendants_list}")
    return


#添加一个查询自己是否是管理员的功能
check_self = on_command('我是管理员吗',
                        aliases={"检查管理", "check_admin", "checkadmin"},
                        block=True,
                        priority=5)


@check_self.handle()
async def handle_check_self(bot: Bot, event: GroupMessageEvent):
    user_id = event.get_user_id()
    group_id = event.group_id
    intendant_util = IntendantInformation(group_id)

    if intendant_util.is_intendant(user_id):
        await bot.send(event, "您是当前群组的管理员")
    else:
        await bot.send(event, "您不是当前群组的管理员")
    return