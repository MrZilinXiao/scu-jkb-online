import json
from datetime import datetime

import pytz
import requests

from scujkbapp.models import Record, UserProfile
from scujkbapp.config import CONFIG, PROMPT
from wxpusher import WxPusher

header = CONFIG.HEADER


def single_check_in(user: UserProfile):
    jkb = jkbSession(user.stu_id, user.stu_pass, user.wx_uid)  # login here
    try:
        jkb.login()
        old = jkb.get_daily()
        return jkb.submit(old)

    except jkbException as e:
        if e.code == '10001':
            user.valid = False
            user.save()
            jkb.message(PROMPT.WRONG_PASS_TITLE, PROMPT.WRONG_PASS_BODY)
            return PROMPT.WRONG_PASS_TITLE, PROMPT.WRONG_PASS_BODY
        elif e.code == '10002':
            jkb.message(PROMPT.WRONG_YESTERDAY_INFO, PROMPT.WRONG_YESTERDAY_INFO)
            return PROMPT.WRONG_YESTERDAY_INFO, PROMPT.WRONG_YESTERDAY_INFO
        elif e.code == '10003':
            jkb.message(PROMPT.FAIL_CHECKIN, str(e))
            return PROMPT.FAIL_CHECKIN, str(e)
        else:
            raise NotImplementedError


class jkbException(Exception):
    def __init__(self, code, info=''):
        self.codedict = {
            '10001': '学号或密码错误',
            '10002': '昨日信息获取失败',
            '10003': '打卡失败'
        }
        self.code = code
        self.info = info

    def __str__(self):
        try:
            return self.codedict[self.code] + ' ' + self.info
        except KeyError:
            raise Exception("错误代码不存在")


class jkbSession:
    def __init__(self, username, passwd, wx_uid=None):
        self.s = requests.Session()
        self.s.headers.update(header)
        self.wx_uid = wx_uid
        self.username = username
        self.passwd = passwd

    def login(self):
        payload = {
            "username": self.username,
            "password": self.passwd
        }
        r = self.s.post("https://wfw.scu.edu.cn/a_scu/api/sso/check", data=payload)
        if not r.json().get('m') == "操作成功":
            raise jkbException('10001')

    def get_daily(self):
        daily = self.s.get("https://wfw.scu.edu.cn/ncov/api/default/daily?xgh=0&app_id=scu")
        j = daily.json()
        d = j.get('d', None)
        if d:
            return daily.json()['d']
        else:
            raise jkbException('10002')

    def submit(self, old: dict):
        new_daily = {
            'realname': old['realname'],  # 姓名
            'number': old['number'],  # 学工号
            'sfzx': old['sfzx'],  # 是否在校
            'ismoved': old['ismoved'],  # ？所在地点
            'tw': old['tw'],  # 体温
            'sftjwh': old['sftjwh'],  # 是否途经武汉
            'sftjhb': old['sftjhb'],  # 是否途经湖北
            'sfcxtz': old['sfcxtz'],  # 是否出现体征？
            'sfjcwhry': old['sfjcwhry'],  # 是否接触武汉人员
            'sfjchbry': old['sfjchbry'],  # 是否接触湖北人员
            'sfjcbh': old['sfjcbh'],  # 是否接触病患 ？疑似/确诊人群
            'sfcyglq': old['sfcyglq'],  # 是否处于隔离期？
            "sfjxhsjc": old['sfjxhsjc'],  # 是否进行核酸检查 1
            'hsjcjg': old['hsjcjg'],  # 核酸检测结果 2
            "hsjcrq": "2020-09-11",
            "hsjcdd": "四川大学华西医院",
            "szxqmc": "江安校区",
            'sfcxzysx': old['sfcxzysx'],  # 是否出现值得注意的情况？
            'szsqsfybl': old['szsqsfybl'],
            'sfsqhzjkk': old['sfsqhzjkk'],
            'sfygtjzzfj': old['sfygtjzzfj'],
            'old_szdd': old['old_szdd'],  # 所在地点
            'sfsfbh': old['sfsfbh'],  # 是否？？病患
            'geo_api_info': old['old_city'],
            'old_city': old['old_city'],
            'geo_api_infot': old['geo_api_infot'],
            'date': datetime.now(tz=pytz.timezone("Asia/Shanghai")).strftime("%Y-%m-%d"),
            'app_id': 'scu'
        }
        r = self.s.post("https://wfw.scu.edu.cn/ncov/api/default/save", data=new_daily)
        # print("提交信息: ", new_daily)
        # print(r.text)
        result = r.json()
        try:
            new_daily['geo_api_info'] = new_daily['geo_api_info'].replace(r'\\', '\\').encode().decode('unicode_escape').replace('\\', '')
            new_daily['geo_api_infot'] = new_daily['geo_api_infot'].replace(r'\\', '\\').encode().decode('unicode_escape').replace('\\', '')
            new_daily['old_city'] = new_daily['old_city'].replace(r'\\', '\\').encode().decode(
                'unicode_escape').replace('\\', '')
        except:
            print("KeyError")
            pass

        new_daily = json.dumps(new_daily, ensure_ascii=False)
        print("显示信息：" + new_daily)

        if result.get('m') == "操作成功":
            print("打卡成功")
            self.message("打卡成功", "服务器返回：" + new_daily)
        else:
            print("打卡失败，错误信息: ", r.json().get("m"))
            # self.message(result.get('m'), new_daily)
            raise jkbException('10003', result.get('m'))
        return result.get('m'), new_daily

    def message(self, title, body):
        userprofile = UserProfile.objects.get(stu_id=self.username)
        record = Record(user=userprofile, title=title, content=body)
        record.save()
        if self.wx_uid:
            self.wx_message(self.wx_uid, title, body)
        # if self.SCKey:
        #     self.wechat_message(self.SCKey, title, body)

    @staticmethod
    def wx_message(wx_uid, title, body):
        WxPusher.send_message(content=' '.join([title, body]), uids=[wx_uid], url='https://jkb.mrxiao.net/')

    # @staticmethod
    # def wechat_message(key, title, body):
    #     if key:
    #         msg_url = "https://sc.ftqq.com/{}.send?text={}&desp={}".format(key, title, body)
    #         requests.get(msg_url)
