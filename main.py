import pkgutil
from graia.ariadne.app import Ariadne
from graia.ariadne.model import MiraiSession
from graia.saya import Saya
from graia.saya.builtins.broadcast import BroadcastBehaviour
from graia.scheduler.saya.behaviour import GraiaSchedulerBehaviour
from graia.scheduler import GraiaScheduler
app = Ariadne(
    MiraiSession(
        host="http://localhost:8080",
        verify_key="Aa11221133",
        account=202898447,
    ),
)
bcc = app.broadcast
sche = app.create(GraiaScheduler)
saya = app.create(Saya)
saya.install_behaviours(
    app.create(BroadcastBehaviour),
    BroadcastBehaviour(bcc),
    GraiaSchedulerBehaviour(sche)
)

with saya.module_context():
    for module_info in pkgutil.iter_modules(["modules"]):
        if module_info.name.startswith("_"):
            continue
        saya.require("modules." + module_info.name)

app.launch_blocking()
