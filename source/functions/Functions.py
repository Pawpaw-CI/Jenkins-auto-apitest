#coding=utf8

import json
import re
from Sender import Sender
from Function_Library import Local_Functions, RF_Functions, Errors , Out_Log

class Basics:
    status_code = ''
    feed_back = ''
    error_msg = ''
    project_path = ''
    cookie = ''

    def __init__(self, _project_path):
        self.status_code = ''
        self.feed_back = ''
        self.error_msg = ''
        self.project_path = _project_path
        self._loc_f = Local_Functions(LOG)
        self._rf_f = RF_Functions()
        self._global_value_list = []


    def get_info(self, _method, _url, _params):
        _params = self._loc_f.format_input(_params)
        __data, __cookie = self._loc_f.deal_params(_params)
        _sender = Sender()
        _sender.send(_method, _url, __data, __cookie)
        self.status_code = _sender.status_code
        self.feed_back = _sender.feedback
        self.error_msg = _sender.error_msg
        self.cookie = _sender.cookie
        if self.error_msg:
            Errors(self.error_msg)

    def basic_check(self, _method, _url, _params, _input_check=[], _input_global=[]):
        self.get_info(_method, _url, _params)
        LOG.info(unicode('返回值：', encoding='utf8'))
        LOG.info(json.dumps(self.feed_back,ensure_ascii=False))  # 首先打印返回值
        if self.status_code != 200:  # 检查statuscode
            Errors('Error: status code = %s' % self.status_code)
        else:
            LOG.info('Status code = %s, Pass!' % self.status_code)
        if _input_check:
            self._loc_f.deal_check(self.feed_back,_input_check)
        if _input_global:
            self._global_value_list = self._loc_f.deal_global(self.feed_back,_input_global)
        LOG.info(json.dumps(self.feed_back, ensure_ascii=False, indent=4, sort_keys=True))
        if len(self._global_value_list) == 1:
            return self._global_value_list[0]
        else:
            return self._global_value_list

def basic_post(_log_path, _url, _params, _input_check=[], _input_global=[]):
    global LOG
    LOG = Out_Log(_log_path)
    _basic = Basics(_log_path)
    return _basic.basic_check('POST', _url, _params, _input_check, _input_global)

def basic_get(_log_path, _url, _params, _input_check=[], _input_global=[]):
    global LOG
    LOG = Out_Log(_log_path)
    _basic = Basics(_log_path)
    return _basic.basic_check('GET', _url, _params, _input_check, _input_global)

def login(_log_path, _url, _params):
    global LOG
    LOG = Out_Log(_log_path)
    _basic = Basics(_log_path)
    _basic.get_info('POST', _url, _params)
    return _basic.cookie

if __name__=="__main__":
    url='http://172.17.123.139:8090/chiq_webservice/services?appKey=mr3z5f&method=ch.tvmall.chiq.hotkeyword.get&v=2&format=json'
    data=u'{"client":{"agent_name":"tt","agent_ver":"1.0.327","device":"TV",”tv_version”:”ZLM60HiS_0.99999”},"safeFlag": 2}'
    data=u'{"client": {"agent_name": "tt","agent_ver": "1.0.327","device": "TV","tv_version": "ZLS59Gi_9.99999"},"providerCode": "chiq3","version": "5","resIconType": "VER_MIDDLE","searchName": "终结者","sequence":3}'
    check=u'code=1000,serviceMethod'
    glob=u'serviceMethod'
    basic_post('/tmp/django/out.log',url,data,check,glob)

