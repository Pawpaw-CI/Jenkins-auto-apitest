import urllib2
import json
import re

class dailybg:
    def __init__(self):
        self.json=self.get_json()
        self.link='http://cn.bing.com'+self.get_jpg_link()

    def get_json(self):
        req=urllib2.Request(url='http://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1')
        response=urllib2.urlopen(req)
        return json.load(response)

    def get_jpg_link(self):
        func=re.findall(r'u\'url\': u\'(.+?)\',',str(self.json))
        return func[0]

    def download(self):
        req=urllib2.urlopen(self.link)
        data=req.read()
        path = '/tmp/BingDailyWallPaper.jpg'
        with open(path, 'wb') as jpg:
            jpg.write(data)
        req.close()


