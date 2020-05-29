from django import forms
from .models import User
import re
from django.core.validators import RegexValidator


class LoginForm(forms.Form):
    userName = forms.IntegerField(label='Username', error_messages={'required': '学号不能为空'},
                                  widget=forms.TextInput(attrs={'class': 'form-control',
                                                                'placeholder': '学号',
                                                                'autofocus': ''}))
    password = forms.CharField(label='Password', max_length=256,
                               widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                 'placeholder': '密码'}))

    captcha = forms.CharField(label='Captcha', max_length=4, widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                           'placeholder': '验证码'}))

    def clean(self):
        try:
            username = self.cleaned_data['userName']
            password = self.cleaned_data['password']
        except Exception as e:
            print('Error when login: ' + str(e))
            raise forms.ValidationError(u"用户名或密码不符合格式")


class RegForm(forms.Form):
    userName = forms.IntegerField(label='Username', error_messages={'required': '学号不能为空'},
                                  widget=forms.TextInput(attrs={'class': 'form-control',
                                                                'placeholder': '学号',
                                                                'autofocus': ''}))
    SCKey = forms.CharField(label='SCKey', max_length=256,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': 'SCKey（选填）'}))
    password = forms.CharField(label='Password', min_length=6, max_length=256,
                               widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                 'placeholder': '四川大学统一认证密码'}))
    passwordTwice = forms.CharField(label='PasswordTwice', max_length=256,
                                    widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                      'placeholder': '再次输入密码',
                                                                      'onblur': 'validate()'}))

    invitation_key = forms.CharField(label='invitation', max_length=256,
                                     widget=forms.TextInput(attrs={'class': 'form-control',
                                                                   'placeholder': '邀请码'}))

    captcha = forms.CharField(label='Captcha', max_length=4, widget=forms.TextInput(attrs={'class': 'form-control',
                                                                                           'placeholder': '验证码'}))

    def clean(self):  # 检查除了验证码之外的注册信息
        try:
            username = self.cleaned_data['userName']
        except Exception as e:
            print('except: ' + str(e))
            raise forms.ValidationError(u"用户名或邮箱不符合格式")

        # is_username_exist = User.objects.filter(username=username).exists()
        # if is_username_exist:
        #     print('Already Taken')
        #     raise forms.ValidationError(u"用户名或邮箱已被注册")
        try:
            password = self.cleaned_data['password']
        except Exception as e:
            print('except: ' + str(e))
        #     raise forms.ValidationError(u"请输入至少8位密码")
        # try:
        #     phonenumber = self.cleaned_data['phoneNumber']
        #     ret = re.match(r"^1[3456789]\d{9}$", phonenumber)
        #     if not ret:
        #         raise forms.ValidationError
        # except Exception as e:
        #     print('except: ' + str(e))
        #     raise forms.ValidationError(u"手机号码格式不正确")
        return self.cleaned_data
