#coding=utf8
import pymysql
import datetime
from source.robotframework_API import RF_API
from source.local_file import Local
from warnings import filterwarnings
filterwarnings('error', category=pymysql.Warning) #捕获warning
import subprocess

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



class Modify_Database:
    error_msg=''

    def add_new_project(self,projectname):
        _conn=Connection()
        tablename='proj_'+projectname
        _conn.commit("CREATE TABLE IF NOT EXISTS %s (id int(4) NOT NULL PRIMARY KEY AUTO_INCREMENT, "
                                                  " module_name VARCHAR(50) NOT NULL, "
                                                  " testcase_name VARCHAR(50), "
                                                  " function VARCHAR(50),"
                                                  " URL VARCHAR(2560),"
                                                  " data VARCHAR(2560),"
                                                  " vars VARCHAR(256),"
                                                  " globvars VARCHAR(256)) DEFAULT CHARSET=utf8" % tablename)
        if _conn.error_msg:
            self.error_msg=_conn.error_msg
            print 'Error code(%s),%s'%(_conn.error_msg[0],_conn.error_msg[1])
            return False
        else:
            return True

    def remove_project(self,projectname):
        _conn=Connection()
        tablename='proj_'+projectname
        _conn.commit("DROP TABLE IF EXISTS %s"%tablename)
        if _conn.error_msg:
            self.error_msg=_conn.error_msg
            print 'Error code(%s),%s'%(_conn.error_msg[0],_conn.error_msg[1])
            return False
        else:
            return True

    def rename_project(self,projectname,new_projectname):
        _conn=Connection()
        tablename='proj_'+projectname
        new_tablename='proj_'+new_projectname
        _conn.commit("RENAME TABLE %s to %s"%(tablename,new_tablename))
        if _conn.error_msg:
            self.error_msg=_conn.error_msg
            print 'Error code(%s),%s'%(_conn.error_msg[0],_conn.error_msg[1])
            return False
        else:
            return True


    '''def update_project(self,projectname,data):
        _conn=Connection()
        tablename='proj_'+str(projectname)
        if _conn.commit("DELETE FROM %s"%tablename):
            for line in data:
                for i in range(len(line)+1,6):
                    line.append('NULL')
                _conn.commit("INSERT INTO %s (module_name,function,URL,data,vars,globvars) VALUES (%s,%s,%s,%s,%s)"%(
                    tablename,line[0],line[1],line[2],line[3],line[4]
                ))
                if _conn.error_msg:
                    print 'Error code(%s),%s' % (_conn.error_msg[0], _conn.error_msg[1])'''


class SQL_Data:
    error_msg=''
    _project_list=[]
    _module_list=[]
    _testcase_list=[]
    state=True

    def __init__(self):
        self.get_project_list()

    def add_project(self,project_name):
        check_sql='show tables'
        _conn=Connection()
        if _conn.select(check_sql):
            __project_list=_conn.fetchall()
            for tables in __project_list:
                for table in tables:
                    if table==project_name:
                        self.error_msg='该项目已存在，请重新命名'
                        return False
            _edit=Modify_Database()
            if _edit.add_new_project(project_name):
                return True
            else:
                self.error_msg=_edit.error_msg
                return False
            return True
        else:
            self.error_msg=_conn.error_msg
            return False

    def remove_project(self,project_name):
        _edit=Modify_Database()
        if _edit.remove_project(project_name):
            return True
        else:
            self.error_msg=_edit.error_msg
            return False

    def rename_project(self,project_name,new_project_name):
        _conn=Connection()
        check_sql = 'show tables'
        _conn = Connection()
        if _conn.select(check_sql):
            __project_list = _conn.fetchall()
            for tables in __project_list:
                for table in tables:
                    if table == new_project_name:
                        self.error_msg = '该项目已存在，请重新命名'
                        return False
            _edit=Modify_Database()
            if _edit.rename_project(project_name,new_project_name):
                return True
            else:
                self.error_msg = _edit.error_msg
                return False
        else:
            self.error_msg=_conn.error_msg
            return False


    def get_project_list(self):
        sql='show tables'
        _conn=Connection()
        if _conn.select(sql):
            self._project_list=[]
            for table in _conn.fetchall():
                if table[0][0:5] == 'proj_':
                    self._project_list.append(table[0][5:])
        else:
            self.error_msg == _conn.error_msg

    def get_module_list(self, project_name):
        project_name='proj_'+project_name
        sql = 'select module_name from %s group by module_name ORDER BY id'%project_name
        _conn = Connection()
        if _conn.select(sql):
            self._module_list=[]
            for module in _conn.fetchall():
                self._module_list.append(module[0])
        else:
            self.error_msg = _conn.error_msg

    def add_module(self,project_name,new_module_name):
        project_name='proj_'+project_name
        sql_check = "select module_name from %s where module_name=\'%s\'"%(project_name,new_module_name)
        sql = "INSERT INTO %s (module_name) VALUE (\'%s\')"%(project_name,new_module_name)
        _conn=Connection()
        if _conn.select(sql_check):
            if len(_conn.fetchall()) != 0:
                self.error_msg = u'该模块已存在，请重新命名'
                return False
            else:
                if _conn.commit(sql):
                    return True
                else:
                    self.error_msg = _conn.error_msg
                    return False
        else:
            self.error_msg = _conn.error_msg
            return False

    def rename_module(self,project_name,old_module_name,new_module_name):
        project_name='proj_'+project_name
        check_sql="select count(module_name) from %s where module_name=\'%s\'"%(project_name,new_module_name)
        sql="update %s set module_name = \'%s\' where module_name=\'%s\'"%(project_name,new_module_name,old_module_name)
        _conn=Connection()
        if _conn.select(check_sql):
            if _conn.fetchall()[0][0] !=0:
                self.error_msg='已存在该名称的模块，请修改'
                return False
        if _conn.commit(sql):
            return True
        else:
            self.error_msg=_conn.error_msg
            return False

    def remove_module(self,project_name,module_name):
        project_name='proj_'+project_name
        sql="DELETE FROM %s where module_name=\'%s\'"%(project_name,module_name)
        _conn=Connection()
        if _conn.commit(sql):
            return True
        else:
            self.error_msg=_conn.error_msg
            return False

    def get_testcase_list(self,project_name,module_name):
        project_name='proj_'+project_name
        sql='select testcase_name,function,URL,data,vars,globvars from %s where module_name=\'%s\' ORDER BY id '%(project_name,module_name)
        _conn=Connection()
        if _conn.select(sql):
            self._testcase_list=_conn.fetchall()
        else:
            self.error_msg=_conn.error_msg

    def save_testcase(self,project_name,module_name,new_testcase):
        project_name='proj_'+project_name
        sql = 'select id from %s where module_name=\'%s\'' % (project_name, module_name)
        _conn = Connection()
        if _conn.select(sql):
            __id_list = _conn.fetchall()
            id_list = ''
            for ele in __id_list:
                id_list += str(ele[0]) + ','
            id_list = id_list[:-1]
            sql_del = 'DELETE FROM %s where id in (%s)' % (project_name, id_list)
            for ele in new_testcase:
                sql='INSERT INTO %s (module_name,testcase_name,function,URL,data,vars,globvars) VALUES (\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')'%(
                    project_name,module_name,ele[0],ele[1],ele[2],ele[3],ele[4],ele[5])
                if not _conn.commit(sql):
                    self.state = False
                    self.error_msg = _conn.error_msg
            if self.state:
                _conn.commit(sql_del)
        else:
            self.error_msg = _conn.error_msg

    def run(self,project_name,module_list):
        project_name='proj_'+project_name
        time = str(datetime.datetime.now()).split('.')[0]
        _local = Local()
        for module in module_list:
            sql = "select testcase_name,function,URL,data,vars,globvars from %s where module_name =\'%s\' ORDER BY id"%(project_name,module)
            _conn=Connection()
            if _conn.select(sql):
                testcase = _conn.fetchall()
            _local.save_testcase(project_name,module,testcase,time)
            if _local._project_path != '':
                tmp_run = RF_API()
                tmp_run.run(_local._project_path)

            if _local.error_msg == '':
                self._run_project_path=_local._project_path
            else:
                self.error_msg=_local.error_msg
        f = open(_local._project_path + '/out.log', 'r')
        return f.readlines(), _local._project_path


if __name__ == '__main__':
    a=Modify_Database().add_new_project('test')
    b=Modify_Database().update_project('test',[[1,2,3],[1,2,3,4,5]])
    c=Connection()
    c.select('select * from auth_user')
    print c.fetchall()