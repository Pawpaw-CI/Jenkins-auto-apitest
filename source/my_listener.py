#coding=utf8
import os
import traceback
from functions.Function_Library import Out_Log


class my_listener:
    _start = False
    _end = False
    ROBOT_LISTENER_API_VERSION = 2
    _log=''
    _total_test = 0
    _test_cnt = 0

    def __init__(self, *args):
        file_path = args[0]+':'+args[1]+':'+args[2]
        self._log = Out_Log(file_path)
        #self.log_file = open(file_path, 'a+')

    def start_keyword(self,name,attrs):
        self._log._sys('[Start_Keyword]:%s' % (attrs['args']))

    def start_suite(self,name,attrs):
        if self._start == False:
            self._log._sys('[Start_Suite]:[%s] %s Totaltests: %s ' % (attrs['starttime'].split(' ')[1], attrs['suites'] ,attrs['totaltests']))
            self._log._sys('==================================================================================')
            self._total_test = attrs['totaltests']
            self._start = True

    def end_suite(self, name, attrs):
        traceback.print_exc()
        if self._end == False:
            self._log._sys('==================================================================================')
            if attrs['status'] == 'FAIL':
                self._log.error('[End_Suite]:[%s] %s %s' % (attrs['endtime'].split(' ')[1],attrs['status'],repr(attrs['statistics']).replace('\\n',' ')))
            elif attrs['status'] == 'PASS':
                self._log.info('[End_Suite]:[%s] %s %s' % (attrs['endtime'].split(' ')[1],attrs['status'],repr(attrs['statistics']).replace('\\n',' ')))
            else:
                self._log._sys('[End_Suite]:[%s] %s %s' % (attrs['endtime'].split(' ')[1],attrs['status'],repr(attrs['statistics']).replace('\\n',' ')))
            self._end = True

    def start_test(self, name, attrs):
        self._log._sys('[Start_Test]:[%s]' % (attrs['longname']))

    def end_test(self, name, attrs):
        self._test_cnt += 1

        if attrs['status'] == 'FAIL':
            self._log.error('[End_Test]:[%s] %s' % (attrs['longname'],attrs['status']))
        elif attrs['status'] == 'PASS':
            self._log.info('[End_Test]:[%s] %s' % (attrs['longname'],attrs['status']))
        else:
            self._log._sys('[End_Test]:[%s] %s' % (attrs['longname'],attrs['status']))
        if self._test_cnt != self._total_test:
            self._log._sys('------------------------------------------------------------------------------------------------------------------------------')

'''
    def _error(self, _log_message):
        self.log('ERROR', _log_message)

    def _sys(self, _log_message):
        self.log('SYS', _log_message)

    def log(self, _log_level, _log_message):
        print _log_level, _log_message.encode('utf8')
        self.log_file.write("[%s]: %s" % (_log_level, _log_message.encode('utf8'))+'\n')
        self.log_file.flush()
        os.fsync(self.log_file)

    def __del__(self):
        self.log_file.close()'''


