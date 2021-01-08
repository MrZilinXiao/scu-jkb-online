from . import views
from django.conf.urls import url
from scujkbapp.wxpusher import WxPusherCallback, WxPusherQRCode

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.register, name='register'),

    # User Management Module
    url(r'^login/$', views.logIn, name="login"),
    url(r'^logout/$', views.logOut, name="logout"),
    url(r'^check_captcha', views.check_captcha, name="check_captcha"),
    url(r'^checkUsername', views.checkUsername, name="checkUsername"),
    url(r'^check_bind', views.check_bind, name="check_bind"),
    url(r'^inner_index/$', views.inner_index, name='inner_index'),
    url(r'^getRecordList$', views.getRecordList, name="getRecordList"),
    url(r'^test$', views.test, name="test"),
    url(r'^delete$', views.delete, name="delete"),
    url(r'^adjust$', views.adjust, name="adjust"),
    url(r'^wxpusher', WxPusherCallback.as_view(), name='wxpusher'),
    url(r'^get_wx_qrcode', WxPusherQRCode.as_view(), name='wxpusher_qrcode')
]

handler404 = views.page_not_found
handler500 = views.page_error
