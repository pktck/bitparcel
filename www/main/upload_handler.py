from django.core.files.uploadhandler import FileUploadHandler

class BitparcelUploadHandler(FileUploadHandler):
    def __init__(self):
        print 'starting da upload'

    def receive_data_chunk(self, raw_data, start):
        print 'got a chunk:', start

    def file_complete(self, file_size):
        print 'all done! file size:', file_size


