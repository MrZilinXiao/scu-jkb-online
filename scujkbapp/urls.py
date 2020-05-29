from . import views
from django.conf.urls import url

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^register/$', views.register, name='register'),

    # User Management Module
    url(r'^login/$', views.logIn, name="login"),
    url(r'^logout/$', views.logOut, name="logout"),
    url(r'^check_captcha', views.check_captcha, name="check_captcha"),
    url(r'^checkUsername', views.checkUsername, name="checkUsername"),
    url(r'^inner_index/$', views.inner_index, name='inner_index'),
    url(r'^getRecordList$', views.getRecordList, name="getRecordList"),
    url(r'^test$', views.test, name="test"),
    url(r'^delete$', views.delete, name="delete"),

]

handler404 = views.page_not_found
handler500 = views.page_error
