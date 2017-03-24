#coding=utf8
import pymysql
import datetime
from source.robotframework_API import RF_API
from source.local_file import Local
from warnings import filterwarnings
filterwarnings('error', category=pymysql.Warning) #捕获warning
import urlparse
import re
from functions.Function_Library import Errors

class Connection:
    error_msg = ''
    _conn = None
    _cur = None
    _TIMEOUT = 10

    def __init__(self):
        try:
            self._conn=pymysql.connect(host='10.9.50.196',port=3306,
                                       user='root',password='Test#123',db='django_test',charset='utf8')
        except pymysql.Warning, warning:
            self.error_msg=warning
        except pymysql.Error,err:
            self.error_msg=err
        if self.error_msg:
            print 'MySQL connection Failed on %s, %s'%(self.error_msg[0],self.error_msg[1])
        self._cur=self._conn.cursor()

    def select(self,sql):
        try:
            self._cur.execute(sql)
        except pymysql.Warning, warning:
            self.error_msg=warning
        except pymysql.Error,err:
            self.error_msg=err
        if self.error_msg:
            print 'MySQL execute Failed on %s, %s'%(self.error_msg[0],self.error_msg[1])
            return False
        else:
            return True


    def commit(self,sql):
        try:
            result = self._cur.execute(sql)
            self._conn.commit()
        except pymysql.Warning, warning:
            self._conn.rollback()
            self.error_msg = warning
        except pymysql.Error, err:
            self._conn.rollback()
            self.error_msg = err
        if self.error_msg:
            print 'MySQL execute Failed on %s, %s'%(self.error_msg[0],self.error_msg[1])
            return False
        else:
            return True

    def fetchall(self):
        try:
            return self._cur.fetchall()
        except pymysql.Warning, warning:
            self.error_msg = warning
        except pymysql.Error, err:
            self.error_msg = err
        return []

    def close(self):
        try:
            self._cur.close()
            self._conn.close()
        except:
            pass
    def __del__(self):
        self.close()


def run(_project_name, _url=''):
    project_name ='proj_'+_project_name.decode('utf8')
    time = str(datetime.datetime.now()).split('.')[0]
    _local = Local()
    _conn = Connection()
    sql_get_module = 'select module_name from %s group by module_name' % project_name
    _conn.select(sql_get_module)
    module_list = _conn.fetchall()
    for module in module_list:
        module = module[0]
        sql = "select testcase_name,function,URL,data,vars,globvars from %s where module_name=\'%s\' ORDER BY id"\
              % (project_name, module)
        if _conn.select(sql):
            testcase = _conn.fetchall()
            if _url:
                _url = modify_url(testcase[0][2], _url)
            _local.save_testcase(project_name, module, testcase, time)
        if _local._project_path != '':
            tmp_run = RF_API()
            tmp_run.run(_local._project_path)
        if _local.error_msg:
            Errors(_local.error_msg)
            break
    return _local._project_path

def modify_url(exist_url, new_url):
    if re.findall(r'(?=<//).*(?=:)', exist_url):
        _tmp_url = urlparse.urlunparse(exist_url)
        out_len = len(_tmp_url.scheme)+3+len(_tmp_url.netloc)
        return new_url+exist_url[out_len:]

if __name__ == '__main__':
    run('我')