from django.apps import AppConfig
from wxpusher import WxPusher
from scujkbapp.config import CONFIG


class ScujkbappConfig(AppConfig):
    name = 'scujkbapp'

    def ready(self):
        WxPusher.default_token = CONFIG.WXPUSHER_API_TOKEN
        print('WxPusher Ready')
