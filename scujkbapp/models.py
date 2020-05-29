from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class UserProfile(models.Model):
    uid = models.AutoField(primary_key=True)
    stu_id = models.CharField('学号', max_length=13)
    stu_pass = models.CharField('密码', max_length=64)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='UserProfile', unique=True)
    SCKey = models.CharField('SCKey', max_length=128, default='')
    vaild = models.BooleanField('是否有效', default=True)

    class Meta:
        verbose_name = '个人信息'


class Record(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='Record')
    addTime = models.DateTimeField('时间', auto_now_add=True)
    title = models.CharField('标题', max_length=512, default='')
    content = models.CharField('返回信息', max_length=512, default='')

    class Meta:
        verbose_name = '打卡记录'


class Invitation(models.Model):
    code = models.CharField('邀请码', max_length=1000)
    usedBy = models.CharField('被谁使用', max_length=1000, default='')
    addBy = models.CharField('由谁加入', max_length=1000, default='')
    createTime = models.DateTimeField('添加时间', auto_now_add=True)
    usedTime = models.CharField('使用时间', max_length=1000)
