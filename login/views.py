#coding=utf-8
from django.shortcuts import render,render_to_response,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib import messages
from django.template.context import RequestContext
from django.forms.formsets import formset_factory
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.contrib.auth.decorators import login_required
from django import forms
from django.views.decorators.csrf import csrf_exempt
from main_page.dailybg import dailybg


class LoginForm(forms.Form):
    username = forms.CharField(label='',max_length=30,widget=forms.TextInput(
        attrs={
            'class':'form-control',
            'placeholder':u'请输入用户名',
            'style': 'margin-bottom:10px',
               }
    ))
    password = forms.CharField(label='',widget=forms.PasswordInput(
        attrs={

            'class':'form-control',
            'placeholder':u'请输入密码',
        }
    ))

    def clean(self):
        if self.is_valid():
            cleaned_data = super(LoginForm, self).clean()

class RegisterForm(forms.Form):
    username = forms.CharField(label='',max_length=30,widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': u'请输入用户名',
            'style': 'margin-bottom:10px',
        }
    ))
    password1 = forms.CharField(label='', widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': u'请输入密码',
            'style': 'margin-bottom:10px',
        }
    ))
    password2 = forms.CharField(label='', widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': u'请确认密码',
            'style': 'margin-bottom:10px',
        }
    ))
    userrealname = forms.CharField(label='', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': u'请输入姓名',
            'style': 'margin-bottom:10px',
        }
    ))

    def clean(self):
        if self.is_valid():
            cleaned_data = super(RegisterForm, self).clean()




@csrf_exempt
def login(request):
    if request.method=='GET':
        return render_to_response('login/login.html', RequestContext(request,{'form':LoginForm,'wallpaper':dailybg().link}))
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect('/main_page/')
            else:
                return render_to_response('login/login.html',
                                              RequestContext(request, {'form': form, 'password_is_wrong': True}))
        else:
            return render_to_response('login/login.html', RequestContext(request, {'form': form, }))

        render_to_response('main_page/main_page.html',RequestContext(request))

@csrf_exempt
def register(request):
    if request.method=='GET':
        return render_to_response('login/register.html', RequestContext(request,{'form':RegisterForm,'wallpaper':dailybg().link}))
    else:
        username,password1,password2,userrealname=request.POST.get('registerinfo').split(';')
        form = RegisterForm({'username':username, 'password1':password1, 'password2':password2, 'userrealname':userrealname})
        if form.is_valid():
            errors=[]
            if password1 != password2:
                errors.append(u'两次输入密码不同')
            filterresult = User.objects.filter(username=username)
            if len(filterresult) > 0:
                errors.append(u'用户名已存在')
            if len(errors) != 0:
                print errors
                return HttpResponse(errors)
            else:
                user = User()
                user.username = username
                user.set_password(password2)
                user.first_name = userrealname.encode('utf8')
                user.is_staff = True
                data=['注册成功']
                user.save()
                return HttpResponse(data)
        else:
            render_to_response('login/register.html', RequestContext(request, {'form': RegisterForm, 'error':'illegal','wallpaper':dailybg().link}))
