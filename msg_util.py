import re
from typing import Union

from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent

"""
来源：https://github.com/yzyyz1387/nonebot_plugin_admin/blob/main/nonebot_plugin_admin/message.py#L42
"""


async def get_msg_text(event: GroupMessageEvent) -> str:
    """
    提取群消息中的纯文本内容

    Args:
        event: 群消息事件对象

    Returns:
        str: 消息中的纯文本部分
    """
    return event.get_plaintext()


async def get_msg_text_no_url(event: GroupMessageEvent) -> str:
    """
    提取群消息中的纯文本内容，并移除所有URL链接和空白字符

    Args:
        event: 群消息事件对象

    Returns:
        str: 移除URL和空白后的纯文本
    """
    msg = event.get_plaintext()
    # 移除所有HTTP/HTTPS链接
    no_url = re.sub(r'https?://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]', '', msg)
    # 移除所有空白字符（包括空格、换行、制表符等）
    return re.sub(r'\s+', '', no_url)


async def get_msg_img(event: GroupMessageEvent) -> list:
    """
    提取群消息中的图片/表情链接

    Args:
        event: 群消息事件对象

    Returns:
        list: 包含图片URL的列表，支持普通图片和QQ表情(mface)
    """
    img = []
    for msg in event.message:
        if msg.type in ['image', 'mface']:
            img.append(msg.data['url'])
    return img


async def get_msg_raw(bot: Bot, event: GroupMessageEvent) -> str:
    """
    获取消息的原始处理版本，将媒体内容转换为文本表示

    Args:
        bot: NoneBot实例
        event: 群消息事件对象

    Returns:
        str: 处理后的原始消息文本

    Note:
        - 图片会被转换为OCR识别文本或图片URL
        - 合并转发消息会展开为转发内容的所有原始消息
        - 其他特殊消息类型会被转换为对应的数据表示
    """
    raw = event.raw_message
    for msg in event.message:
        if msg.type in ['image', 'mface']:
            if msg.type == 'image':
                try:
                    # 尝试使用OCR识别图片中的文字
                    res = await bot.call_api(api='ocr_image', image=msg.data['url'])
                    # 将图片替换为OCR识别出的文字
                    raw = raw.replace(str(msg), ' ' + ' '.join([i['text'] for i in res['texts']]) + ' ', 1)
                    continue
                except Exception:
                    # OCR失败则回退到使用图片URL
                    pass
            # 非图片的媒体或OCR失败时使用URL替换
            raw = raw.replace(str(msg), ' ' + msg.data['url'] + ' ', 1)
        elif msg.type == 'forward':  # 合并转发不可能与其他消息结合
            try:
                # 获取合并转发的详细内容
                forward = await bot.get_forward_msg(id=msg.data['id'])
                # 将所有转发消息的原始内容拼接
                return ' '.join([i['raw_message'] for i in forward['messages']])
            except Exception:
                break
    return raw


async def get_msg_at(event: GroupMessageEvent) -> list:
    """
    提取群消息中@的QQ号

    Args:
        event: 群消息事件对象

    Returns:
        list: 被@的QQ号列表
    """
    qq = []
    for msg in event.message:
        if msg.type == 'at':
            qq.append(msg.data['qq'])
    return qq


async def get_msg_reply(event: GroupMessageEvent) -> Union[int, None]:
    """
    获取消息回复的消息ID

    Args:
        event: 群消息事件对象

    Returns:
        Union[int, None]: 回复的消息ID，如果消息不是回复则返回None
    """
    return event.reply.message_id if event.reply else None