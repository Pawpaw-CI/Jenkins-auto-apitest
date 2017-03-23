#coding=utf8
from robot import run_cli
import sys,os
import tempfile
class RF_API:

    def run(self,project_path):
        log_path = str(project_path.encode('utf8'))+'out.log'
        run_cli(['--outputdir', project_path, '--listener', os.path.dirname(os.path.abspath(__file__))+'/my_listener.py:'+log_path, project_path], exit = False)
