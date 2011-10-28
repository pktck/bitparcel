from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import render_to_response
from helpers import Helper
import StringIO

helper = Helper()

def front(req):
    return render_to_response('front.html', locals())


def upload(req):
    thefile = req.FILES['thefile']
    
    file_sender = helper.storeFile(thefile.name)

    chunk_count = 0

    for chunk in thefile.chunks():
        #chunk = StringIO.StringIO(chunk)
        file_sender.addChunk(chunk)
        chunk_count += 1

    print 'chunk count:', chunk_count

    download_key = file_sender.completeUpload()

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


