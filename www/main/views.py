from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import render_to_response
from helpers import Helper

helper = Helper()

def front(req):
    return render_to_response('front.html', locals())


def upload(req):
    thefile = req.FILES['thefile']

    download_key = helper.storeFile(thefile)

    return HttpResponse(req.build_absolute_uri('%s/%s' % (download_key, thefile.name)), mimetype='text/plain')


def download(req, download_key, filename):
    row = helper.getRow(download_key)
    url_filename = row.filename.replace(' ', '-')
    if (not filename) or (filename != url_filename):
        return HttpResponseRedirect('/%s/%s' % (download_key, url_filename))
    
    file_url = '/files/%s/%s' % (download_key, row.file_key)

    return render_to_response('download.html', locals())
   

def downloadFile(req, download_key, file_key):
    row = helper.getRow(download_key)
    if row.file_key != file_key:
        raise Exception("Download_key and file_key don't match.")

    thefile = helper.getFile(file_key)

    response = HttpResponse(thefile.read(), mimetype='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s' % row.filename
    return response
 
