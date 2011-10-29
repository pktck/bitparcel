from django.core.files.uploadhandler import FileUploadHandler
from django.core.files.uploadedfile import UploadedFile
from helpers import Helper

helper = Helper()

class BitparcelUploadHandler(FileUploadHandler):
    def __init__(self):
        print 'starting da upload'

    def new_file(self, field_name, file_name, content_type, content_length, charset):
        self.file_sender = helper.storeFile(file_name)
        self.file_name = file_name

    def receive_data_chunk(self, raw_data, start):
        print 'got a chunk:', start
        self.file_sender.addChunk(raw_data)

    def file_complete(self, file_size):
        download_key = self.file_sender.completeUpload()
        print 'all done! file size:', file_size
        uploaded_file = UploadedFile()
        uploaded_file.download_key = download_key
        uploaded_file.name = self.file_name
        return uploaded_file

