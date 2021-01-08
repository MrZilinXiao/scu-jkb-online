import time
import random
from scujkbapp.models import UserProfile
from scujkbapp.jkb import single_check_in


def cronJob():
    userList = UserProfile.objects.filter(valid=True)
    for user in userList:
        single_check_in(user)
        time.sleep(random.random() * 5)  # 0 ~ 5s gap
