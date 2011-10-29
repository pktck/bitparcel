from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import render_to_response
from helpers import Helper
from django.views.decorators.csrf import csrf_exempt
from upload_handler import BitparcelUploadHandler

helper = Helper()

def front(req):
    return render_to_response('front.html', locals())

@csrf_exempt
def upload(req):
    req.upload_handlers = [BitparcelUploadHandler()]
    
    thefile = req.FILES['thefile']
    download_key = thefile.download_key
    
    return HttpResponse(req.build_absolute_uri('%s/%s' % (download_key, thefile.name.replace(' ', '-'))), mimetype='text/plain')


def download(req, download_key, filename):
    row = helper.getRow(download_key)
    url_filename = row.filename.replace(' ', '-')
    if (not filename) or (filename != url_filename):
        return HttpResponseRedirect('/%s/%s' % (download_key, url_filename))
    
    file_url = '/files/%s/%s/%s' % (download_key, row.file_key, row.filename)

    return render_to_response('download.html', locals())
   

def downloadFile(req, download_key, file_key, filename):
    row = helper.getRow(download_key)
    if row.file_key != file_key:
        raise Exception("Download_key and file_key don't match.")
    if row.filename != filename:
        raise Exception("Download_key and file_key don't match filename.")

    #thefile = helper.getFile(file_key)
    key_obj = helper.getKeyObj(file_key)

    #response = HttpResponse(thefile.read(), mimetype='application/octet-stream')
    response = HttpResponse(key_obj, mimetype='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s' % row.filename
    response['Content-Length'] = row.size
    return response


