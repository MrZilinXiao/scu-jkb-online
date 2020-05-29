import datetime
import random
import string
import time
import scujkbapp.jkb as jkb

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from scujkbapp.forms import LoginForm, RegForm
from scujkbapp.models import UserProfile, Invitation, Record


def page_not_found(request, exception):
    return render(request, '404.html', status=404)


def page_error(request):
    return render(request, '500.html', status=500)


def index(request):
    if request.user.is_authenticated:
        user = request.user
        username = user.username

        return render(request, 'index.html', locals())
    else:
        return redirect('login')


def logIn(request):
    if request.user.is_authenticated:
        return redirect(request.META.get('HTTP_REFERER', '/'))
    if request.method == 'GET':
        form = LoginForm()
        request.session['login_from'] = request.META.get('HTTP_REFERER',
                                                         '/')
        return render(request, 'login.html', locals())
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        errormsg = ''
        if form.is_valid():
            username = str(form.cleaned_data['userName'])
            password = form.cleaned_data['password']
            captcha = form.cleaned_data['captcha'].strip()
            if username != '' and password != '' and captcha == request.session['CheckCode'].lower():
                user = authenticate(username=username, password=password)
                if user is not None:
                    UserQ = User.objects.get(username=username)
                    # if UserQ.UserProfile.is_active:
                    login(request, user)  # 调用login方法登陆账号
                    return redirect(request.session['login_from'])
                    # else:
                    #     errormsg = "用户未激活！"
                elif captcha != request.session['CheckCode'].lower():
                    errormsg = "验证码错误"
                else:
                    errormsg = "用户名或密码错误"
            elif username == '' or password == '':
                errormsg = "用户名或密码不能为空"
            else:
                errormsg = "其他错误"
        return render(request, 'login.html', locals())


def check_captcha(request):
    import io
    from . import check_captcha as CheckCode
    stream = io.BytesIO()
    # img 图片对象, code 在图像中写的内容
    img, code = CheckCode.create_validate_code()
    img.save(stream, "png")
    # 图片页面中显示, 立即把 session 中的 CheckCode 更改为目前的随机字符串值
    request.session["CheckCode"] = code
    return HttpResponse(stream.getvalue())


def register(request):
    if request.method == 'GET':
        form = RegForm()
        request.session['login_from'] = request.META.get('HTTP_REFERER',
                                                         '/')
        return render(request, 'register.html', locals())
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            form = RegForm(request.POST)
            errormsg = ''
            if form.is_valid():
                username = form.cleaned_data['userName']
                password = form.cleaned_data['password']
                SCKey = form.cleaned_data['SCKey']
                invitation = form.cleaned_data['invitation_key']
                captcha = form.cleaned_data['captcha']
                if username != '' and password != '' and captcha == request.session['CheckCode'].lower():
                    if User.objects.filter(username=username).exists():
                        errormsg = '学号已存在，如果您忘记了密码，请联系管理员'
                    else:
                        # 检查统一平台密码
                        try:
                            auth = jkb.jkbSession(username, password)
                        except jkb.jkbException as e:
                            errormsg = str(e)
                            return render(request, 'register.html', locals())
                        try:
                            invitation_list = Invitation.objects.get(code=invitation)
                        except Exception:  # 0 or more than 1
                            errormsg = '邀请码有误'
                            return render(request, 'register.html', locals())
                            # return render(request, 'register.html', locals(), {'form': form})

                        if invitation_list.usedBy != '':
                            errormsg = '邀请码已被使用'
                            return render(request, 'register.html', locals())

                        invitation_list.usedBy = str(username)
                        invitation_list.usedTime = time.strftime("%Y-%m-%d %H:%M:%S")
                        invitation_list.save()

                        user = User.objects.create_user(username=username, password=password)
                        userProfile = UserProfile(user=user, stu_pass=password)
                        userProfile.save()
                        user.backend = 'django.contrib.auth.backends.ModelBackend'
                        login(request, user)
                        return redirect('index')
                elif captcha != request.session['CheckCode'].lower():
                    errormsg = '验证码错误'
                return render(request, 'register.html', locals())
            else:
                return render(request, 'register.html', {'form': form})
        else:
            return redirect('index')


@login_required
def logOut(request):
    try:
        logout(request)
    except Exception as e:
        print(e)
    return redirect(request.META['HTTP_REFERER'])


def checkUsername(request):
    user_name = request.GET.get('userName')
    if User.objects.filter(username=user_name).exists():
        return HttpResponse(1)
    else:
        return HttpResponse(0)


def inner_index(request):
    if request.user.is_authenticated:
        return render(request, 'index_v1.html', locals())
    else:
        return redirect('login')


@login_required
def getRecordList(request):
    def utc2local(utc_st):
        # UTC时间转本地时间（+8:00）
        now_stamp = time.time()
        local_time = datetime.datetime.fromtimestamp(now_stamp)
        utc_time = datetime.datetime.utcfromtimestamp(now_stamp)
        offset = local_time - utc_time
        local_st = utc_st + offset
        return local_st

    userprofile = UserProfile.objects.get(stu_id=request.user.username)
    if request.method == 'GET':
        try:
            page_record = []
            page = request.GET.get('page')
            num = request.GET.get('rows')
            right_boundary = int(page) * int(num)
            recordSet = Record.objects.filter(user=userprofile)
            for i, record in enumerate(recordSet):
                local_time = utc2local(record.addTime)
                LOCAL_FORMAT = "%Y-%m-%d %H:%M:%S"
                create_time_str = local_time.strftime(LOCAL_FORMAT)
                single_code = {'id': i + 1, 'title': record.title, 'content': record.content,
                               'createTime': create_time_str}
                page_record.append(single_code)
            total = len(recordSet)
            page_record = page_record[int(num) * (int(page) - 1):right_boundary]
            return JsonResponse({'total': total, 'rows': page_record})  # 一点骚操作，异步前端操作真的不熟
        except Exception as e:
            raise e