from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import render_to_response
from helpers import BitparcelDownload, DownloadSession
from django.views.decorators.csrf import csrf_exempt
from upload_handler import BitparcelUploadHandler


def front(req):
    return render_to_response('front.html', locals())


@csrf_exempt
def upload(req):
    req.upload_handlers = [BitparcelUploadHandler()]

    thefile = req.FILES['thefile']
    
    file_uri = '%s/%s' % (thefile.download_key, thefile.name.replace(' ', '-'))
    file_url = req.build_absolute_uri(file_uri)

    return HttpResponse(file_url, mimetype='text/plain')


def download(req, download_key, filename):
    row = BitparcelDownload.getRow(download_key)

    url_filename = row.filename.replace(' ', '-')
    if (not filename) or (filename != url_filename):
        return HttpResponseRedirect('/%s/%s' % (download_key, url_filename))

    if row.downloads >= 5:
        return render_to_response('too_many_downloads.html', locals())

    download_session_key = DownloadSession.create()

    file_url = '/files/%s/%s/%s/%s' % (download_key, row.file_key, download_session_key, row.filename)

    return render_to_response('download.html', locals())
   

def downloadFile(req, download_key, file_key, download_session_key, filename):
    bitparcel_download = BitparcelDownload(download_key, file_key, download_session_key, filename)

    response = HttpResponse(bitparcel_download.getChunkyKeyObj(), mimetype='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename="%s"' % bitparcel_download.row.filename
    response['Content-Length'] = bitparcel_download.row.size

    return response


def progress(req, download_session_key):
   downloaded_size = DownloadSession.get(download_session_key).downloaded_size
   return HttpResponse('{"downloaded_size": %s}' % downloaded_size, mimetype='application/json')


