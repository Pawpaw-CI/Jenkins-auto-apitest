#coding=utf8
from robot.libraries.BuiltIn import BuiltIn
import re
import json
import os


class RF_Functions:

    error_msg = ''

    def __init__(self):
        self.error_msg = ''

    def get_global_value(self,_var1,_var2):
        if _var1[1] in '@$&':
            _var1 = BuiltIn().get_variable_value(_var1)
        if _var2[1] in '@$&':
            _var2 = BuiltIn().get_variable_value(_var2)
        return _var1,_var2


class Local_Functions:

    error_msg = ''
    _project_path = ''
    LOG = ''

    def __init__(self, _log):
        self.error_msg = ''
        self.LOG = _log

    def scheme(self, _scheme):
        pass

    @staticmethod
    def format_input(_input):
        _input = _input.encode('utf8')
        _input = _input.replace('\\n', '"')
        _input = _input.replace('”', '"')
        _input = _input.replace('“', '"')
        _input = _input.replace('’', '\'')
        _input = _input.replace('‘', '\'')
        _input = _input.replace('，', ',')
        _input = _input.replace(' ', '')
        _input = _input.decode('utf8')
        return _input

    def deal_params(self, params):
        cookie = re.findall(r'cookie={(.*)},{', params)
        if cookie:
            cookie = cookie[0]
        else:
            cookie = re.findall(r'cookie={(.*)}', params)
            if cookie:
                cookie = cookie[0]
            else:
                cookie = ''
                data = params.encode('utf8')
                return data, cookie
        whole_cookie = 'cookie={'+cookie+'}'
        cookie = cookie.split(';')
        cookies = {}
        for single in cookie:
            key, value = single.split('=', 1)
            cookies[key] = value
        _index = params.index(whole_cookie)
        if _index == 0:
            data = params[len(whole_cookie)+1:]
        else:
            data = params[:_index-1]
        if data:
            data = eval(data.encode('utf8'))
        return data, cookies



    def deal_check(self, feedback_json, _input_check):
        _check_list = _input_check.split(',')
        __tmp = self.grep_data(feedback_json, _check_list)
        for ele in _check_list:
            cnt = 0
            if re.search(r'[!<>=]+', ele) is None:  # 有对比值的进入比较功能
                self.LOG.info(unicode('[ %s ] 取值查询: %s' % (str(ele), __tmp[cnt]), encoding='utf8'))
                cnt += 1

    def deal_global(self, feedback_json, _input_global):
        _check_list = _input_global.split(',')
        _global_var_list=[]
        for ele in _check_list:
            _global_var_list.append(ele)
        return self.grep_data(feedback_json, _global_var_list)

    def grep_data(self, feedback_json, _check_list):
        _return_list = []
        for element in _check_list:
            if re.search(r'[!<>=]+', element) is not None:  # 有对比值的进入比较功能
                self.compare(feedback_json, element)
            else:  # 没对比值的直接查找
                try:
                    tempinfo = re.findall(r'(?:\'' + element + '\':)([^,]+)+', str(feedback_json))
                    if tempinfo:
                        # 优化输出格式
                        if len(tempinfo) == 1:
                            _return_list.append(tempinfo[0])
                        else:
                            _return_list.append(tempinfo)
                    else:
                        self.LOG.error(u'关键字检查中未找到[ %s ]数据,请核实' % element)
                        Errors(u'关键字检查中未找到[ %s ]数据,请核实' % element)
                except Exception, err:
                    self.LOG.error(err)
        return _return_list  # to do may be

    def compare(self, feedback_json, _input):
        _symbol_list = re.findall(r'[!<>=]+', _input)
        if len(_symbol_list) == 1:
            _a_value = re.search(r'[^!<>=]+', _input).group()
            symbol = _symbol_list[0]
            _b_value = re.search(r'[^!<>=]+$', _input).group()
            _rf_f=RF_Functions()  # 获取global值
            _a_value,_b_value=_rf_f.get_global_value(_a_value,_b_value)

            _a_feedback = re.findall(r'(?:\'' + _a_value + '\':)([^,]+)+', str(feedback_json))
            if not _a_feedback:
                _b_feedback = re.findall(r'(?:\'' + _b_value + '\':)([^,]+)+', str(feedback_json))
                if not _b_feedback:
                    self.LOG.error(u'关键字检查中未找到[ %s ]数据,请核实' % _input)
                    Errors(u'关键字检查未找到变量[ %s ]数据，请检查' % _input)
                else:
                    _return_data = _b_feedback
                    if self.compare_detail(_a_value, symbol, _b_feedback):
                        self.LOG.info(unicode('[ %s ] 返回值为： %s, Pass!' % (_input.encode('utf8'), _return_data), encoding='utf8'))
                    else:
                        self.LOG.error(u'[ %s ]结果与预期不匹配，具体算式：%s, %s, %s' % (_input, _a_value, symbol, _b_feedback))
                        Errors(u'[ %s ]结果与预期不匹配，具体算式：%s, %s, %s' % (_input, _a_value, symbol, _b_feedback))

            else:
                _return_data = _a_feedback
                if self.compare_detail(_a_feedback, symbol, _b_value):
                    self.LOG.info(unicode('[ %s ] 返回值为： %s, Pass!' % (_input.encode('utf8'), _return_data), encoding='utf8'))
                else:
                    self.LOG.error(u'[ %s ]结果与预期不匹配，具体算式：%s, %s, %s' % (_input, _a_feedback, symbol, _b_value))
                    Errors(u'[ %s ]结果与预期不匹配，具体算式：%s, %s, %s' % (_input, _a_feedback, symbol, _b_value))

        elif len(_symbol_list) == 2:
            _value_list = re.findall(r'[^!<>=]+', _input)
            _feedback = re.findall(r'(?:\'' + _value_list[1] + '\':)([^,]+)+', str(feedback_json))  # 存疑！
            if not _feedback:
                self.LOG.error(u'关键字检查未找到变量[ %s ]数据，请检查' % _input)
                Errors(u'关键字检查未找到变量[ %s ]数据，请检查' % _input)
            else:
                _return_data = _feedback
                for i in range(2):
                    if self.compare_detail(_value_list[i], _symbol_list[i], _value_list[i + 1]):
                        self.LOG.info(unicode('[ %s ] 返回值为： %s, Pass!' % (_input.encode('utf8'), str(_return_data)),encoding='utf8'))
                    else:
                        self.LOG.error(u'[ %s ]结果与预期不匹配，具体算式：%s, %s, %s' % (
                            _input, _value_list[i], _symbol_list[i], _value_list[i + 1]))

                        Errors(u'[ %s ]结果与预期不匹配，具体算式：%s, %s, %s' % (
                            _input, _value_list[i], _symbol_list[i], _value_list[i + 1]))

    def compare_detail(self, _avalue, _symbol, _bvalue):
        _cmp=[]
        if _symbol == '>':
            _cmp = [1]
        elif _symbol == '<':
            _cmp = [-1]
        elif _symbol == '=':
            _cmp = [0]
        elif _symbol == '!=':
            _cmp = [1, -1]
        elif _symbol == '<=':
            _cmp = [0, -1]
        elif _symbol == '>=':
            _cmp = [0, 1]
        else:
            self.LOG.error(u'关键字检查中，符号有误，请检查，只支持（ <, >, =, !=, <=, >= ）')
            Errors(u'关键字检查中，符号有误，请检查，只支持（ <, >, =, !=, <=, >= ）')
        if type(_avalue) == list:
            for ele in _avalue:
                if cmp(str(ele).strip(' ').strip('u').strip('\''), _bvalue) not in _cmp:
                    return False
            return True
        if type(_bvalue) == list:
            for ele in _bvalue:
                if cmp(_avalue, str(ele).strip(' ').strip('u').strip('\'')) not in _cmp:
                    return False
            return True
        if cmp(str(_avalue).strip(' ').strip('u').strip('\''), str(_bvalue).strip(' ').strip('u').strip('\'')) in _cmp:
            return True
        else:
            return False


class Errors:
    def __init__(self, error_msg, error_type=ValueError):
        error = error_type(error_msg)
        error.ROBOT_CONTINUE_ON_FAILURE = True
        raise error


class Out_Log(object):
    _file = ''

    def __init__(self, _log_path):
        self._file=open(_log_path, 'a+')

    def info(self, _log_message):
        self.log('INFO', _log_message)

    def error(self, _log_message):
        self.log('ERROR', _log_message)

    def _sys(self, _log_message):
        self.log('SYS', _log_message)

    def log(self, _log_level, _log_message):
        print _log_level, _log_message.encode('utf8')
        self._file.write("[%s]: %s" % (_log_level, _log_message.encode('utf8'))+'\n')
        self._file.flush()
        os.fsync(self._file)

    def __del__(self):
        self._file.close()
