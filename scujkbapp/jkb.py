import json
from datetime import datetime

import pytz
import requests

from scujkbapp.models import Record, UserProfile

header = {"User-Agent": "Mozilla/5.0 (Linux; Android 10;"
                        "  AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 "
                        "Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045136 Mobile "
                        "Safari/537.36 wxwork/3.0.16 MicroMessenger/7.0.1 "
                        "NetType/WIFI Language/zh", }


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
    def __init__(self, username, passwd, SCKey=''):
        self.s = requests.Session()
        self.s.headers.update(header)
        self.SCKey = None
        self.username = username
        payload = {
            "username": username,
            "password": passwd
        }
        r = self.s.post("https://wfw.scu.edu.cn/a_scu/api/sso/check", data=payload)
        if not r.json().get('m') == "操作成功":
            raise jkbException('10001')
        if SCKey:
            self.SCKey = SCKey

    def get_daily(self):
        daily = self.s.get("https://wfw.scu.edu.cn/ncov/api/default/daily?xgh=0&app_id=scu")
        # info = s.get("https://app.ucas.ac.cn/ncov/api/default/index?xgh=0&app_id=ucas")
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
            "sfjxhsjc": old['sfjxhsjc'],  # 是否进行核酸检查
            'sfcxzysx': old['sfcxzysx'],  # 是否出现值得注意的情况？
            'szsqsfybl': old['szsqsfybl'],
            'sfsqhzjkk': old['sfsqhzjkk'],
            'sfygtjzzfj': old['sfygtjzzfj'],
            'hsjcjg': old['hsjcjg'],
            'old_szdd': old['old_szdd'],  # 所在地点
            'sfsfbh': old['sfsfbh'],  # 是否？？病患
            'geo_api_info': old['old_city'],
            'old_city': old['old_city'],
            'geo_api_infot': old['geo_api_infot'],
            'date': datetime.now(tz=pytz.timezone("Asia/Shanghai")).strftime("%Y-%m-%d"),
            'app_id': 'scu'
        }
        r = self.s.post("https://wfw.scu.edu.cn/ncov/api/default/save", data=new_daily)
        print("提交信息: ", new_daily)
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
        if self.SCKey:
            self.wechat_message(self.SCKey, title, body)

    @staticmethod
    def wechat_message(key, title, body):
        if key:
            msg_url = "https://sc.ftqq.com/{}.send?text={}&desp={}".format(key, title, body)
            requests.get(msg_url)
