from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from scujkbapp.config import CONFIG
from scujkbapp.models import UserProfile
from wxpusher import WxPusher
import json


class WxPusherCallback(View):
    def post(self, request):
        """
        Example POST payload:
        {
          "action":"app_subscribe",//动作，app_subscribe 表示用户关注应用回调，后期可能会添加其他动作，请做好兼容。
          "data":{
              "appId":123,//创建的应用ID
              "appKey":"AK_xxxxxx", //关注应用的appKey，请不要再使用，将来可能会被删除
              "appName":"应用名字",
              "source":"scan", //用户关注渠道，scan表示扫码关注，link表示链接关注，command表示通过消息关注应用，后期可能还会添加其他渠道。
              "userName":"wxpusher",
              "userHeadImg":"http://xxxxx/132",//最后一个数值代表正方形头像大小（有0、46、64、96、132数值可选，0代表640*640正方形头像），用户没有头像时该项为空
              "time":1569416451573, //消息发生时间
              "uid":"UID_xxxxxx", //用户uid
              "extra":"xxx"    //用户扫描带参数的二维码，二维码携带的参数。扫描默认二维码为空
          }
        }
        """
        data_payload = json.loads(request.body)
        data_action = data_payload['action']
        data = data_payload['data']
        if data['appId'] != CONFIG.WXPUSHER_APPID:
            raise RuntimeError("回调APPID校验错误！")
        if data_action == 'app_subscribe':
            uid, user_param = data['uid'], data['extra']
            user_profile = UserProfile.objects.get(stu_id=user_param)  # raise DoesNotExist if with no luck
            user_profile.wx_uid = uid
            user_profile.valid = True
            user_profile.save()

            WxPusher.send_message("SCU健康报绑定成功，请继续在平台上进行相关操作，并阅读使用说明。", uids=[uid])

        else:
            raise NotImplementedError

    @csrf_exempt  # disable CSRF
    def dispatch(self, request, *args, **kwargs):
        return super(WxPusherCallback, self).dispatch(request, *args, **kwargs)


class WxPusherQRCode(View):
    def get(self, request):
        extra = request.user.username
        # {'code': 1000, 'msg': '处理成功',
        # 'data':
        # {'expires': 1610079780214,
        # 'code': 'VTofGQDeSo3ezYYfzs1akLQ0vCTKqvM5O35z9iey2TdknDiwQRhdaUhEa98u9vEW',
        # 'shortUrl': 'https://mmbizurl.cn/s/Ognm4CzsM',
        # 'extra': 'hello',
        # 'url':
        # 'https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=gQE38DwAAAAAAAAAAS5odHRwOi8vd2VpeGluLnFxLmNvbS9xLzAyNFpSSFZNSVFjWWoxWUF1VE52Y1QAAgQc1-dfAwQIBwAA'},
        # 'success': True}
        payload = WxPusher.create_qrcode(extra=extra, valid_time=600)
        return JsonResponse(payload)
