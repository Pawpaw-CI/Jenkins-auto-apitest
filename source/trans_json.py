#coding=utf8
import json
class Json_Transfer:

    def to_json(self,bool,data):
        dict={'state':bool,'data':data}
        return json.dumps(dict)

    def auto_sender(self,error_msg,data):
        if error_msg != '':
            error=error_msg
            return self.to_json(False,error)
        else:
            return self.to_json(True,data)