from django.http import FileResponse
from urlparse import urlparse

def get_result(request):
    if request.method == 'GET':
        link=request.path[8:]
        print link
        return FileResponse(open(link,'rb'))