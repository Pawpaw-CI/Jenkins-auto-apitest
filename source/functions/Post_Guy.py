#coding=utf8
import urllib2
import json
import re
import time
from urlparse import urlparse
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from Function_Library import Errors


def send(url,params):
    #ip,port,url,sign,time,token,params 需要用random_test脚本自动浮动测试
    #random_test(url,params)
    headers = {'Content-Type': 'application/json'}
    try:
        req = urllib2.Request(url=url,headers=headers,data=json.dumps(params))
        response = urllib2.urlopen(req)
        statuscode= response.getcode()
        jsondata=json.load(response)
        return statuscode,jsondata
    except Exception,err:
        print err

def struct_url(scheme,ip,port,path,sign,time,token):
    url=scheme+'://'+ip+':'+str(port)+path+'?sign='+sign+'&time='+time+'&token='+token
    return url

def basic_check(url, params, specialinput=[], globalinput=[]):   #自动发放多个data ，无法对比code
    params=params.encode('utf8').replace('”','"')
    params=params.decode('utf8')
    params=eval(params)

    #特殊变量求值
    if specialinput != []:
        special=True
        specialvars=specialinput.split(',')
    else:
        special=False
    #global
    if globalinput != []:
        glob=True
        globalvars=globalinput.split(',')
    else:
        glob=False
    #----正常发送----
    statuscode, jsondata=send(url,params)
    normaljsondata=jsondata
    if statuscode != 200:
        print u'Status = [ %d ]'%statuscode
        Errors(u'Status=%d'%statuscode)
    else:
        print u'通过：'
        print u'正确发送data内容 %s : Statu: %d, Code: %s'%(params, statuscode, grep_data(jsondata,['code']))
        if special:
            speciallist=grep_data(jsondata,specialvars)
            try:
                for i in range(len(specialvars)):
                    print u'目标变量： %s, %s'%(specialvars[i],speciallist[i])
            except Exception,e:
                print e

        print u'返回数据体：'
        print json.dumps(jsondata,ensure_ascii=False)
        print '-----------------------------------------------------'
    #----data null----
    tempparams={}
    statuscode,jsondata=send(url,tempparams)
    if statuscode != 200:
        print u'Status = [ %d ]' % statuscode
        Errors(u'Status=%d' % statuscode)
    else:
        print u'通过： '
        print u'异常发送data内容为空， Statu: %d, Code: %s'%(statuscode, grep_data(jsondata,['code']))
        print u'返回数据体：'
        print json.dumps(jsondata,ensure_ascii=False)
        print '-----------------------------------------------------'
    #----Wrong data----
    tempparams = params.copy()
    tempparams.popitem()
    statuscode, jsondata = send(url, tempparams)
    if statuscode != 200:
        print u'Status = [ %d ]' % statuscode
        Errors(u'Status=%d' % statuscode)
    else:
        print u'通过 ：'
        print u'异常发送data内容为 %s : Statu: %d, Code: %s' % (tempparams, statuscode, grep_data(jsondata,['code']))
        print u'返回数据体：'
        print json.dumps(jsondata,ensure_ascii=False)
        print '-----------------------------------------------------'

    print u'Pretty Print Json(正常data):'
    print json.dumps(normaljsondata, ensure_ascii=False, indent=4 ,sort_keys=True)
    if glob:
        return grep_data(normaljsondata,globalvars)



def single_check(url, params, specialinput=[], globalinput=[]):  #只发指定data方便对比code
    params=eval(params)
    #特殊变量求值
    if specialinput != []:
        special=True
        specialvars=specialinput.split(',')
    else:
        special=False
    #global
    if globalinput != []:
        glob=True
        globalvars=globalinput.split(',')
    else:
        glob=False
    #----正常发送----
    statuscode, jsondata=send(url,params)
    normaljsondata=jsondata
    if statuscode != 200:
        print u'Status = [ %d ]'%statuscode
        Errors(u'Status=%d'%statuscode)
    else:
        print u'通过：'
        print u'正确发送data内容 %s : Statu: %d, Code: %s'%(params, statuscode, grep_data(jsondata,['code']))
        if special:
            speciallist=grep_data(jsondata,specialvars)
            try:
                for i in range(len(specialvars)):
                    print u'目标变量： %s, %s'%(specialvars[i],speciallist[i])
            except Exception,e:
                print e

        print u'返回数据体：'
        print json.dumps(jsondata,ensure_ascii=False)
        print '-----------------------------------------------------'

    print u'Pretty Print Json:'
    print json.dumps(normaljsondata, ensure_ascii=False, indent=4 ,sort_keys=True)
    if glob:
        return grep_data(normaljsondata,globalvars)

def grep_data(_jsondata,_speciallist):
    list=[]
    for element in _speciallist:
        if re.search(r'[!<>=]+',element) != None:
            list.append(compare(_jsondata,element))
        else:
            try:
                tempinfo=re.findall(r'(?:\''+element+'\':)([^,]+)+',str(_jsondata))
                if tempinfo != []:
                    #优化输出格式
                    if len(tempinfo) == 1:
                        list.append(tempinfo[0])
                    else:
                        list.append(tempinfo)
                else:
                    print u'关键字检查中未找到 [ %s ] 对应字段,请核实'%element
                    Errors(u'关键字检查中未找到%s对应字段,请核实'%element)

            except Exception,e:
                print e
    #优化输出格式
    if len(list) == 1:
        return list[0]
    else:
        return list

def compare(_jsondata, _input):
    symbollist=re.findall(r'[!<>=]+',_input)
    if len(symbollist) == 1:
        avalue=re.search(r'[^!<>=]+', _input).group()
        symbol=symbollist[0]
        bvalue=re.search(r'[^!<>=]+$', _input).group()
        afeedback=re.findall(r'(?:\'' + avalue + '\':)([^,]+)+', str(_jsondata))
        if afeedback == []:
            bfeedback=re.findall(r'(?:\'' + bvalue + '\':)([^,]+)+', str(_jsondata))
            if bfeedback == []:
                print u'关键字检查未找到变量 [ %s] 数据，请检查'%_input
                Errors(u'关键字检查未找到变量%s数据，请检查'%_input)
            else:
                returndata=bfeedback
                if compare_detail(avalue,symbol,bfeedback):
                    print u'[ %s ] 检查通过！'%_input
                else:
                    print u'[ %s ]结果与预期不匹配，具体算式：%s, %s, %s'%(_input,avalue, symbol, bfeedback)
                    Errors(u'[ %s ]结果与预期不匹配，具体算式：%s, %s, %s'%(_input,avalue, symbol, bfeedback))

        else:
            returndata=afeedback
            if compare_detail(afeedback,symbol,bvalue):
                print u'[ %s ] 检查通过！' % _input
            else:
                print u'[ %s ]结果与预期不匹配，具体算式：%s, %s, %s' % (_input, afeedback, symbol, bvalue)
                Errors(u'[ %s ]结果与预期不匹配，具体算式：%s, %s, %s'%(_input,afeedback, symbol, bvalue))



    elif len(symbollist) == 2:
        valuelist=re.findall(r'[^!<>=]+',_input)
        feedback=re.findall(r'(?:\'' + valuelist[1] + '\':)([^,]+)+', str(_jsondata))
        if feedback == []:
            print u'关键字检查未找到变量 [ %s] 数据，请检查' % _input
            Errors(u'关键字检查未找到变量%s数据，请检查' % _input)
        else:
            returndata=feedback
            for i in range(2):
                if compare_detail(valuelist[i],symbollist[i],valuelist[i+1]):
                    print u'[ %s ] 检查通过！'%_input
                else:
                    print u'[ %s ]结果与预期不匹配，具体算式：%s, %s, %s'%(_input,valuelist[i], symbollist[i], valuelist[i+1])
                    Errors(u'临时报错 研究中')
    return returndata

def compare_detail(_avalue,_symbol,_bvalue):
    if _symbol == '>':
        _cmp=[1]
    elif _symbol == '<':
        _cmp=[-1]
    elif _symbol == '=':
        _cmp=[0]
    elif _symbol == '!=':
        _cmp=[1,-1]
    elif _symbol == '<=':
        _cmp=[0,-1]
    elif _symbol == '>=':
        _cmp=[0,1]
    else:
        print u'关键字检查中，符号有误，请检查，只支持（ <, >, =, !=, <=, >= ）'
        Errors(u'关键字检查中，符号有误，请检查，只支持（ <, >, =, !=, <=, >= ）')
    if type(_avalue) == list:
        for ele in _avalue:
            if cmp(str(ele).strip(' ').strip('u').strip('\''), _bvalue) in _cmp:
                return True
            else:
                return False
    if type(_bvalue) == list:
        for ele in _bvalue:
            if cmp(_avalue, str(ele).strip(' ').strip('u').strip('\'')) in _cmp:
                return True
            else:
                return False
    if cmp(str(_avalue).strip(' ').strip('u').strip('\''),str(_bvalue).strip(' ').strip('u').strip('\'')) in _cmp:
        return True
    else:
        return False

def random_test(url,params):
    depart=urlparse(url)
    scheme=depart.scheme
    ip=depart.hostname
    port=depart.port
    path=depart.path
    query=depart.query
    sign=query.split('&')[0].split('=')[1]
    time=query.split('&')[1].split('=')[1]
    token=query.split('&')[2].split('=')[1]
    print scheme, ip, port, path, sign, time, token

    struct_url(scheme,ip,port,path,sign,time,token)


'''
url="http://114.55.62.60:8080/hdserver/usermaterial/materialList?sign=878dc69cb7d2ffe782d03522ee5eb283&time=145861356569&token=515e5bc44714804646645db6c4869476"
data="{'miId':'2','dateTime':'2016-09-18'}"
spec='createTime,weight=23,message=success'
globalinput='${a}=code'


url='http://58.220.29.201/chiq_webservice/services?appKey=mr3z5f&method=ch.tvmall.chiq.voice.search&v=2&format=json'
data=u'{"client":{"agent_name":"tt","agent_ver":"1.0.327","device":"TV",”tv_version”:”ZLM60HiS_0.99999”},"safeFlag": 2}'
data=u'{"client": {"agent_name": "tt","agent_ver": "1.0.327","device": "TV","tv_version": "ZLS59Gi_9.99999"},"providerCode": "chiq3","version": "5","resIconType": "VER_MIDDLE","searchName": "终结者","sequence":3}'
print basic_check(url,data,'code=1001')
'''
