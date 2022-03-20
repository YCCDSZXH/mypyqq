from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group

from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

channel = Channel.current()

@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def ero(app: Ariadne, group: Group, message: MessageChain):
    await app.sendGroupMessage(1004634397, MessageChain.create(
        f"不要说{message.asDisplay()}，来点涩图"
    ))