import random
import string

from scujkbapp.models import Invitation


def generate_code(length=16, n=200):
    """生成n个长度为len的随机序列码"""
    random.seed()
    chars = string.ascii_letters + string.digits
    return [''.join([random.choice(chars) for _ in range(length)]) for _ in range(n)]


def addInvitation(num: int):
    codeList = generate_code(16, num)
    for code in codeList:
        codesave = Invitation(code=code)
        codesave.save()
        print(code)
