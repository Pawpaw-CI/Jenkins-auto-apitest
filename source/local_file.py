#coding=utf-8
import os

class Local:
    _home_path = ''
    error_msg = ''
    _project_path = ''

    def __init__(self):
        self._home_path = '/tmp/django/'

    def add_new_project(self, project_name, timestamp):
        try:
            self._project_path = self._home_path+project_name+'/'+timestamp+'/'
            os.makedirs(self._project_path)
        except Exception, err:
            print err
            self.error_msg = err

    def save_testcase(self, project_name, module_name, testcase, timestamp):
        try:
            self._project_path = self._home_path+project_name+'/'+timestamp+'/'
            __file_name = module_name+'.txt'
            __file_path = self._project_path+__file_name
            if not os.path.exists(self._project_path):
                self.add_new_project(project_name, timestamp)
            _file = open(__file_path, 'w')
            self.stuct_testcase(_file, testcase)
            _file.close()
            return True

        except Exception, err:
            print err
            self.error_msg = err
            return False


    def stuct_testcase(self,__file,testcase):
        __function_path=os.path.dirname(os.path.abspath(__file__))+'/functions/Functions.py'
        __log_path=self._project_path+'out.log'
        __file.write('*** Settings ***'+'\n')
        __file.write('Library           requests' +'\n')
        __file.write('Library           RequestsLibrary'+'\n')
        __file.write('Library           Collections'+'\n')
        __file.write('Library           '+__function_path+'\n')
        __file.write('\n')
        __file.write('*** Test Cases ***'+'\n')
        for line in testcase:
            _global = False
            __globalvars = []
            __globalvaluelist = ''
            if line[5] != '':
                _global = True
                _tmp=line[5].split(',')
                for _ele in _tmp:
                    __globalvars.append(_ele.split('=')[0])
                    __globalvaluelist = __globalvaluelist+_ele.split('=')[1]+','
                __globalvaluelist = __globalvaluelist[:-1]
            cnt = 0
            for elements in line:
                elements = elements.replace(' ', '')
                if elements is None:
                    continue
                if type(elements) == int:
                    elements = str(elements)
                # 差异化输出
                if line[1] in ('basic_post', 'basic_post'):
                    if cnt == 0:
                        __file.write(elements.encode('utf8')+'\n')
                        if _global:
                            for __globalvar in __globalvars:
                                __file.write('    '+__globalvar.encode('utf8'))
                    elif _global and cnt == 5:
                        __file.write('    '+__globalvaluelist.encode('utf8')+'\n')
                        for __globalvar in __globalvars:
                            __file.write('    ' + 'Set Suite Variable'+'    '+__globalvar+'\n')
                    else:
                        __file.write('    '+elements.encode('utf8'))
                        if cnt == 1 and elements in ('basic_post','basic_get'):
                            __file.write('    '+__log_path.encode('utf8'))
                    cnt += 1
                elif line[1] == 'login':
                    if cnt == 0:
                        __file.write(elements.encode('utf8')+'\n')
                        __file.write('    ${cookie}')
                    elif cnt == 5:
                        __file.write('\n')
                        __file.write('    ' + 'Set Suite Variable'+'    ${cookie}'+'\n')
                    else:
                        __file.write('    '+elements.encode('utf8'))
                        if cnt == 1:
                            __file.write('    '+__log_path.encode('utf8'))
                    cnt += 1
                else:
                    if cnt == 0:
                        __file.write(elements.encode('utf8')+'\n')
                    elif cnt == 5:
                        __file.write('\n')
                    else:
                        __file.write('    '+elements.encode('utf8'))
                    cnt += 1



            __file.write('\n')
            __file.write('\n')


