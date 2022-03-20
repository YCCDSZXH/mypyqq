from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage,FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group, MiraiSession, Friend,Member
from graia.ariadne.event.mirai import NudgeEvent
import random
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
bcc = app.broadcast

# @bcc.receiver(GroupMessage)
# async def setu(app: Ariadne, group: Group, message: MessageChain):
#    if str(message) == "你好":
#       await app.sendMessage(
#          group,
#          MessageChain.create(f"不要说{message.asDisplay()}，来点涩图"),
#       )
# @bcc.receiver(NudgeEvent)
# async def getup(app: Ariadne, target: Union[Group, Friend]):
#     # msg = MessageChain.create("你不要光天化日之下在这里戳我啊")
#     # await app.sendMessage(target, msg)
#     await app.sendMessage(
#        target,
#        MessageChain.create(f"不要说，来点涩图"),
#     )


@bcc.receiver(FriendMessage)
async def test(app: Ariadne, friend: Friend, message: MessageChain):
    await app.sendMessage(
       friend,
       MessageChain.create(f"不要说，来点涩图"),
    )

@bcc.receiver(
    GroupMessage,
    dispatchers=[Twilight([FullMatch("好大的奶")])]
)
async def create_forward(app: Ariadne, member: Member,group : Group):
    fwd_nodeList = [
        ForwardNode(
            target=member,
            time=datetime.now(),
            message=MessageChain.create('123456'),
        )
    ]
    # group = GroupMessage.group
    member_list = await app.getMemberList(group)
    for _ in range(3):
        random_member: Member = random.choice(member_list)
        fwd_nodeList.append(
            ForwardNode(
                target=random_member,
                time=datetime.now(),
                message=MessageChain.create("好大的奶"),
            )
        )
    message = MessageChain.create(Forward(nodeList=fwd_nodeList))
    await app.sendGroupMessage(group, message)

app.launch_blocking()
