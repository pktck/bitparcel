from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import render_to_response
from helpers import BitparcelDownload, DownloadSession
from django.views.decorators.csrf import csrf_exempt
from upload_handler import BitparcelUploadHandler


def front(req):
    return render_to_response('front.html', locals())


@csrf_exempt
def upload(req):
    print 'pre'
    req.upload_handlers = [BitparcelUploadHandler()]
    print 'post'
    
    thefile = req.FILES['thefile']
    print 'poster'
    
    file_uri = '%s/%s' % (thefile.download_key, thefile.name.replace(' ', '-'))

    print thefile.download_key, thefile.name

    print 'file_uri:', file_uri

    file_url = req.build_absolute_uri(file_uri)

    print 'file_url:', file_url

    return HttpResponse(file_url, mimetype='text/plain')


def download(req, download_key, filename):
    row = BitparcelDownload.getRow(download_key)
    print 'row:', row
    url_filename = row.filename.replace(' ', '-')
    if (not filename) or (filename != url_filename):
        return HttpResponseRedirect('/%s/%s' % (download_key, url_filename))
    
    download_session_key = DownloadSession.create()

    file_url = '/files/%s/%s/%s/%s' % (download_key, row.file_key, download_session_key, row.filename)

    return render_to_response('download.html', locals())
   

def downloadFile(req, download_key, file_key, download_session_key, filename):
    bitparcel_download = BitparcelDownload(download_key, file_key, download_session_key, filename)

    response = HttpResponse(bitparcel_download.getChunkyKeyObj(), mimetype='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s' % bitparcel_download.row.filename
    response['Content-Length'] = bitparcel_download.row.size

    return response


def progress(req, download_session_key):
   downloaded_size = DownloadSession.get(download_session_key).downloaded_size
   return HttpResponse('{"downloaded_size": %s}' % downloaded_size, mimetype='application/json')


