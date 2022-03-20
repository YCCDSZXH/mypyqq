from pathlib import Path
import requests
import re
from typing import List, Union
import asyncio

from random import randint
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Friend
from graia.broadcast.interrupt import InterruptControl
from graia.broadcast.interrupt.waiter import Waiter
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[FriendMessage], decorators=[MatchContent("welearn")]))
async def ero2(app: Ariadne, friend: Friend):
    inc = InterruptControl(app.broadcast)
    async def friend_print(msg):
        await app.sendFriendMessage(friend, MessageChain.create(msg))

    @Waiter.create_using_function([FriendMessage])
    async def waitForInput(f: Friend, msg: MessageChain):
        if friend.id == f.id:
            return msg.asDisplay()
    async def startwaitInput(send_msg,timeout1 = 30):
        await app.sendFriendMessage(friend, MessageChain.create(send_msg))
        try:
            ret_msg = await inc.wait(waitForInput,timeout=timeout1)
            return ret_msg
        except asyncio.exceptions.TimeoutError:
            await app.sendFriendMessage(friend, MessageChain.create("已超时取消"))
            return "errortimeout"
        

    msg_to_print = ""
    username = await startwaitInput("你好欢迎使用welearn刷课工具\n请输入账号")
    if username == "errortimeout":
        return
    password = await startwaitInput("请输入密码")
    if password == "errortimeout":
        return
    await friend_print("正在登录...")
    loginUrl = "https://sso.sflep.com/cas/login?service=http%3a%2f%2fwelearn.sflep.com%2fuser%2floginredirect.aspx"
    session = requests.Session()
    response = session.get(loginUrl)
    lt = re.search('name="lt" value="(.*?)"', response.text).group(1)
    response = session.post(loginUrl, data={"username": username,"password": password,"lt": lt,"_eventId": "submit","submit": "LOGIN"})
    if "请登录" in response.text:
        msg_to_print+="登录失败\n"
        return
    else:
        msg_to_print+="登录成功,开始查询课程\n"
    url = "https://welearn.sflep.com/ajax/authCourse.aspx?action=gmc"
    response = session.get(
        url, headers={"Referer": "https://welearn.sflep.com/student/index.aspx"})
    if '\"clist\":[]}' in response.text:
        msg_to_print+= '发生错误!!!可能是登录错误或没有课程!!!\n'
        return
    else:
        msg_to_print+= '查询课程成功!!!您的课程:\n\n'
    back = response.json()["clist"]
    for i, course in enumerate(back, start=1):
       msg_to_print+= f'[NO.{i:>2}] 完成度{course["per"]:>3}% {course["name"]}\n'
    order = await startwaitInput(msg_to_print+"\n请输入需要完成的课程序号\n（上方[]内的数字）: ")
    if order == "errortimeout":
        return
    order = int(order)
    cid = back[order - 1]["cid"]
    url = f"https://welearn.sflep.com/student/course_info.aspx?cid={cid}"
    response = session.get(url)

    uid = re.search('"uid":(.*?),', response.text).group(1)
    classid = re.search('"classid":"(.*?)"', response.text).group(1)

    url = 'https://welearn.sflep.com/ajax/StudyStat.aspx'
    response = session.get(url,params={'action':'courseunits','cid':cid,'uid':uid},headers={'Referer':'https://welearn.sflep.com/student/course_info.aspx'})
    back = response.json()['info']

    # 选择单元
    msg_to_print=""
    msg_to_print+='[NO. 0]  按顺序完成全部单元课程\n'
    unitsnum = len(back)
    for i,x in enumerate(back,start=1):
        if x['visible']=='true':
            msg_to_print+= f'[NO.{i:>2d}]  [已开放]  {x["unitname"]}  {x["name"]}\n'
        else:
            msg_to_print+=f'[NO.{i:>2d}] ![未开放]! {x["unitname"]}  {x["name"]}\n'

    unitidx = await startwaitInput(msg_to_print+'请选择需要完成的单元序号（上方[]内的数字，输入0为按顺序刷全部单元）:  ')
    msg_to_print=""
    if unitidx == "errortimeout":
        return
    unitidx = int(unitidx)
    inputcrate = await startwaitInput('模式1:每个练习指定正确率，请直接输入指定的正确率\n如:希望每个练习正确率均为100，则输入 100\n\n模式2:每个练习随机正确率，请输入正确率上下限并用英文逗号隔开\n如:希望每个练习正确率为70～100，则输入 70,100\n\n请严格按照以上格式输入每个练习的正确率: ')
    if inputcrate == "errortimeout":
        return
    if ',' in inputcrate:
        mycrate=eval(inputcrate)
        randommode=True
    else:
        mycrate=inputcrate
        randommode=False
        way1Succeed, way2Succeed, way1Failed, way2Failed = 0, 0, 0, 0

    ajaxUrl = "https://welearn.sflep.com/Ajax/SCO.aspx"
    infoHeaders = {
        "Referer": f"https://welearn.sflep.com/student/course_info.aspx?cid={cid}",
    }

    if(unitidx == 0):
        i = 0
    else:
        i = unitidx - 1
        unitsnum = unitidx

    while True:
        response = session.get(
            f'https://welearn.sflep.com/ajax/StudyStat.aspx?action=scoLeaves&cid={cid}&uid={uid}&unitidx={i}&classid={classid}', headers=infoHeaders)

        if "异常" in response.text or "出错了" in response.text:
            break
        index = 0
        for course in response.json()["info"]:
            if course['isvisible']=='false':  # 跳过未开放课程
                msg_to_print+= f'[!!跳过!!]{index}'
            elif "未" in course["iscomplete"]:  # 章节未完成
                msg_to_print+= f'[即将完成]{index}'
                if randommode is True:
                    crate=str(randint(mycrate[0],mycrate[1]))
                else:
                    crate=mycrate
                data = '{"cmi":{"completion_status":"completed","interactions":[],"launch_data":"","progress_measure":"1","score":{"scaled":"'+crate+'","raw":"100"},"session_time":"0","success_status":"unknown","total_time":"0","mode":"normal"},"adl":{"data":[]},"cci":{"data":[],"service":{"dictionary":{"headword":"","short_cuts":""},"new_words":[],"notes":[],"writing_marking":[],"record":{"files":[]},"play":{"offline_media_id":"9999"}},"retry_count":"0","submit_time":""}}[INTERACTIONINFO]'

                id = course["id"]
                session.post(ajaxUrl, data={"action": "startsco160928",
                                            "cid": cid,
                                            "scoid": id,
                                            "uid": uid
                                            },
                             headers={"Referer": f"https://welearn.sflep.com/Student/StudyCourse.aspx?cid={cid}&classid={classid}&sco={id}"})
                response = session.post(ajaxUrl, data={"action": "setscoinfo",
                                                       "cid": cid,
                                                       "scoid": id,
                                                       "uid": uid,
                                                       "data": data,
                                                       "isend": "False" },
                                        headers={"Referer": f"https://welearn.sflep.com/Student/StudyCourse.aspx?cid={cid}&classid={classid}&sco={id}"})
                msg_to_print+=f'正确率:{crate:>3}%  '
                if '"ret":0' in response.text:
                    msg_to_print+="方式1:成功!!!   "
                    way1Succeed += 1
                else:
                    msg_to_print+="方式1:失败!!!   "
                    way1Failed += 1

                response = session.post(ajaxUrl, data={"action": "savescoinfo160928",
                                                       "cid": cid,
                                                       "scoid": id,
                                                       "uid": uid,
                                                       "progress": "100",
                                                       "crate": crate,
                                                       "status": "unknown",
                                                       "cstatus": "completed",
                                                       "trycount": "0",
                                                       },
                                        headers={"Referer": f"https://welearn.sflep.com/Student/StudyCourse.aspx?cid={cid}&classid={classid}&sco={id}"})
            #    sleep(1) # 延迟1秒防止服务器压力过大
                if '"ret":0' in response.text:
                    msg_to_print+="方式2:成功!!!   "
                    way2Succeed += 1
                else:
                    msg_to_print+="方式2:失败!!!   "
                    way2Failed += 1
            else:  # 章节已完成
                msg_to_print+= f'[ 已完成 ]{index}'
            index+=1
            if index % 25 == 0:
                await friend_print(msg_to_print)
                msg_to_print = ""

        if unitidx != 0:
            break
        else:
            i += 1
    if unitidx == 0:
        return
    else:
        await friend_print(msg_to_print+'\n本单元运行完毕!')
        msg_to_print = ""
        url = "https://welearn.sflep.com/ajax/authCourse.aspx?action=gmc"
        response = session.get(
        url, headers={"Referer": "https://welearn.sflep.com/student/index.aspx"})
        if '\"clist\":[]}' in response.text:
            msg_to_print+= '发生错误!!!可能是登录错误或没有课程!!!\n'
            return
        else:
            msg_to_print+= '您的课程:\n\n'
        back = response.json()["clist"]
        for i, course in enumerate(back, start=1):
           msg_to_print+= f'[NO.{i:>2}] 完成度{course["per"]:>3}% {course["name"]}\n'
        await friend_print(msg_to_print)
