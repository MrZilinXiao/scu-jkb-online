import time

from scujkbapp.jkb import jkbSession, jkbException
from scujkbapp.models import UserProfile


def cronJob():
    userList = UserProfile.objects.filter(vaild=True)
    for user in userList:
        try:
            jkb = jkbSession(user.stu_id, user.stu_pass, user.SCKey)
            old = jkb.get_daily()
            jkb.submit(old)

        except jkbException as e:
            if e.code == '10001':
                user.vaild = False
                user.save()
                jkbSession.wechat_message(user.SCKey, '密码错误', '您在统一认证平台的密码已更改，请登录平台重新修改密码为当前密码')
            if e.code == '10002':
                jkb.message('昨日信息获取错误', '昨日信息获取错误')
            if e.code == '10003':
                jkb.message('打卡失败', str(e))

        time.sleep(0.5)
