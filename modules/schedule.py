from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.saya import Channel
from graia.scheduler import timers
from graia.scheduler.saya.schema import SchedulerSchema

channel = Channel.current()

channel.name("Wyy")
channel.description("网易云时间提醒器")
channel.author("GraiaX")


@channel.use(SchedulerSchema(timers.crontabify("0 0 * * *")))
async def wyy(app: Ariadne):
    await app.sendGroupMessage(1919810, MessageChain.create("现在是网易云时间"))