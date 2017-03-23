#coding=utf-8
from django.shortcuts import render,render_to_response,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect,FileResponse,HttpResponseForbidden
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from source.trans_json import Json_Transfer
import json
from django.contrib import auth

from source.database import SQL_Data

auto_send=Json_Transfer().auto_sender


@csrf_exempt
def basic_page(request):
    _project_list = []
    _module_list = []
    _testcase_list = []
    error_msg = ''

    if request.method == 'GET':
        user = auth.get_user(request)
        if user.is_authenticated():
            print request.GET,'@@get',
            msgtype=request.GET.get('msgtype')
            msgdata=request.GET.getlist('msgdata[]')
            if msgtype == 'select-project':
                print '@select-project'
                _data=SQL_Data()
                _data.get_module_list(msgdata[0])
                _module_list=_data._module_list
                for ele in _testcase_list:
                    while len(ele) != 6:
                        ele.append('NULL')
                return HttpResponse(auto_send(_data.error_msg,_module_list))

            elif msgtype == 'select-module':
                print '@select-module'
                _data=SQL_Data()
                _data.get_testcase_list(msgdata[0],msgdata[1])
                _testcase_list=_data._testcase_list
                for ele in _testcase_list:
                    while len(ele) != 6:
                        ele.append('NULL')
                return HttpResponse(auto_send(_data.error_msg,_testcase_list))

            elif msgtype == 'get_result':
                print '@get-result'
                return FileResponse(open(msgdata[0],'rb'))

            else:
                print '@main'
                #获取project信息
                _data=SQL_Data()
                error_msg=_data.error_msg
                _project_list=_data._project_list


                for ele in _testcase_list:
                    while len(ele) != 6:
                        ele.append('NULL')
                return render_to_response('main_page/main_page.html',RequestContext(
                    request,{'project_list':_project_list,
                             'module_list':_module_list,
                             'testcase_list':_testcase_list,
                             'error_msg':error_msg,
                             'user_name':user.first_name}))
        else:
            return HttpResponseForbidden()

    elif request.method == 'POST':
        print request.POST,'＃＃post'
        msgtype=request.POST.get('msgtype')
        msgdata=request.POST.getlist('msgdata[]')
        user = auth.get_user(request)
        if user.is_authenticated():
            if msgtype == 'add-module':
                print '＃add-module'
                _data=SQL_Data()
                if _data.add_module(msgdata[0],msgdata[1]):
                    _data.get_module_list(msgdata[0])
                    _module_list = _data._module_list
                    for ele in _testcase_list:
                        while len(ele) != 6:
                            ele.append('NULL')
                    _module_list=json.dumps(_module_list)
                    return HttpResponse(auto_send(_data.error_msg,_module_list))
                else:
                    return HttpResponse(auto_send(_data.error_msg,_module_list))

            elif msgtype == 'save-testcase':
                print '＃save-testcase'
                _data=SQL_Data()
                __tempdata=msgdata[2].split('<*&%>')
                datalist=[]
                for ele in __tempdata:
                    if ele != '':
                        ele = ele.replace('\\n', '')
                        ele = ele.replace('\'','\\\'')
                        datalist.append(ele.split('<%&*>'))
                _data.save_testcase(msgdata[0],msgdata[1],datalist)
                return HttpResponse(auto_send(_data.error_msg, []))

            elif msgtype == 'prepare_run':
                print '#run'
                _data = SQL_Data()
                __module_list = msgdata[1].split(',')
                data = _data.run(msgdata[0],__module_list)
                return HttpResponse(auto_send(_data.error_msg, data))

            elif msgtype == 'log_out':
                print '#log_out'
                __error_msg = ''
                try:
                    auth.logout(request)
                except Exception, __error_msg:
                    pass
                return HttpResponse(auto_send(__error_msg, 'True'))

        else:
            return HttpResponseForbidden()

@csrf_exempt
def proj_manage(request):
    if request.method == 'GET':
        user = auth.get_user(request)
        if user.is_authenticated():
            msgtype = request.GET.get('msgtype')
            msgdata = request.GET.getlist('msgdata[]')

            _data = SQL_Data()
            error_msg = _data.error_msg
            _project_list = _data._project_list
            return render_to_response('main_page/project_manage.html',RequestContext(
                request,{'project_list':_project_list,'error':error_msg,'user_name':user.first_name}))
        else:
            return HttpResponseForbidden()

    elif request.method == 'POST':
        msgtype = request.POST.get('msgtype')
        msgdata = request.POST.getlist('msgdata[]')
        print request.POST
        user = auth.get_user(request)
        if user.is_authenticated():
            if msgtype == 'add_project':
                _data=SQL_Data()
                _data.add_project(msgdata[0])
                return HttpResponse(auto_send(_data.error_msg,[]))

            elif msgtype == 'remove_project':
                _data=SQL_Data()
                _data.remove_project(msgdata[0])
                return HttpResponse(auto_send(_data.error_msg,[]))

            elif msgtype == 'rename_project':
                _data=SQL_Data()
                _data.rename_project(msgdata[0],msgdata[1])
                return HttpResponse(auto_send(_data.error_msg,[]))

            elif msgtype == 'rename_module':
                _data=SQL_Data()
                _data.rename_module(msgdata[0],msgdata[1],msgdata[2])
                return HttpResponse(auto_send(_data.error_msg,[]))

            elif msgtype == 'remove_module':
                _data = SQL_Data()
                _data.remove_module(msgdata[0], msgdata[1])
                return HttpResponse(auto_send(_data.error_msg, []))
        else:
            return HttpResponseForbidden()






