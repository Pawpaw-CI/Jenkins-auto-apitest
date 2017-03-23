# coding=utf8
import urllib2
import json
import requests
import traceback
from robot.libraries.BuiltIn import BuiltIn


class Sender:
    status_code = ''
    feedback = ''
    error_msg = ''
    session = ''
    header = ''
    cookie = ''

    def __init__(self):
        self.session = requests.session()
        self.cookie = BuiltIn().get_variable_value('${cookie}')

    def send(self, _send_method, _url, _params='', cookies='', _header={'Content-Type': 'application/json'}):
        try:
            self.session.header = _header
            _params = _params
            if _send_method == 'GET':
                r = self.session.get(_url, _params, cookies=cookies, timeout=2, verify=False)
            elif _send_method == 'POST':
                r = self.session.post(_url, _params, cookies=cookies, timeout=2, verify=False)
            # noinspection PyBroadException
            try:
                self.feedback = r.json()
            except:
                pass
            self.header = r.headers
            self.cookie = self.session.cookies
            self.status_code = r.status_code
        except Exception, err:
            traceback.print_exc()
            self.error_msg = err

if __name__=='__main__':
    url='http://172.17.123.139:8090/chiq_webservice/services?appKey=mr3z5f&method=ch.tvmall.chiq.hotkeyword.get&v=2&format=json'
    data=u'{"client":{"agent_name":"tt","agent_ver":"1.0.327","device":"TV",”tv_version”:”ZLM60HiS_0.99999”},"safeFlag": 2}'
    data=u'{"client": {"agent_name": "tt","agent_ver": "1.0.327","device": "TV","tv_version": "ZLS59Gi_9.99999"},"providerCode": "chiq3","version": "5","resIconType": "VER_MIDDLE","searchName": "终结者","sequence":3}'
    s = Sender()
    s.send('POST',url,data)
    print s.feedback





