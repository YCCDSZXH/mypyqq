import asyncio

from graia.ariadne.message.parser.base import MatchContent
from graia.broadcast.interrupt import InterruptControl
from graia.broadcast.interrupt.waiter import Waiter
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage,FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group, MiraiSession, Friend,Member
from graia.ariadne.event.mirai import NudgeEvent
import random
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from datetime import datetime
from graia.ariadne.message.element import At, Plain, Image, Forward, ForwardNode
from typing import Union
from graia.ariadne.message.parser.twilight import Twilight,FullMatch
app = Ariadne(
    MiraiSession(
        host="http://localhost:8080",
        verify_key="Aa11221133",
        account=202898447,
        # 此处的内容请按照你的 MAH 配置来填写
    ),
)

inc = InterruptControl(app.broadcast)


class SetuTagWaiter(Waiter.create([GroupMessage])):
    "涩图 tag 接收器"

    def __init__(self, group: Union[Group, int], member: Union[Member, int]):
        self.group = group if isinstance(group, int) else group.id
        self.member = member if isinstance(member, int) else member.id

    async def detected_event(self, group: Group, member: Member, message: MessageChain):
        if self.group == group.id and self.member == member.id:
            return message


async def setu():
    # 都说了，涩图 api 可是至宝，怎么可能轻易给你
    return None

@app.broadcast.receiver(
    GroupMessage,
    dispatchers=[Twilight([FullMatch("好大的奶")])]
)
async def ero(app: Ariadne, group: Group, member: Member, message: MessageChain):
    await app.sendGroupMessage(group, MessageChain.create("你想要什么 tag 的涩图"))
    ret_msg = await inc.wait(SetuTagWaiter(group, member))
    await app.sendGroupMessage(
        group,
        MessageChain.create(
            "Image(data_bytes=await setu(ret_msg.split()))"
        )
    )
app.launch_blocking()