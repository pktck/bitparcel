from django.core.files.uploadhandler import FileUploadHandler
from django.core.files.uploadedfile import UploadedFile
from helpers import FileGetter, bucket, files_table
from NoDB import RowAlreadyExists
import random
import string
import uuid
import StringIO


class FileSender(object):
    def __init__(self, filename):
        self.part_counter = 0

        self.row = self.createNewRow()
   
        file_key = uuid.uuid1().hex

        self.mp = bucket.initiate_multipart_upload(file_key)

        self.row.file_key = file_key
        self.row.filename = filename
        self.row.downloads = 0

    def createNewRow(self):
        # create a new row
        while True:
            try:
                download_key = self.generateDownloadKey()
                row = files_table.createLocked(download_key)
                break
            except RowAlreadyExists:
                continue
    
        return row

    def sendChunk(self, chunk):
        self.part_counter += 1
        chunk_fp = StringIO.StringIO(chunk)
        self.mp.upload_part_from_file(chunk_fp, self.part_counter)

    def completeUpload(self, file_size):
        mp_file_size = sum([part.size for part in self.mp])

        if file_size != mp_file_size:
            raise Exception("Uploaded file size doesn't match computed file size.")

        self.mp.complete_upload()

        # save local metadata
        self.row.size = file_size
        self.row.save()

        return self.row.getKey()

    def generateDownloadKey(self):
        return ''.join([random.choice(string.ascii_letters + string.digits) for i in range(5)])


class BitparcelUploadHandler(FileUploadHandler):
    # S3 minimum part size plus an extra 1 MB since Django's first chunk is smaller than chunk_size
    # (probably because it subtracts headers from the first chunk)
    # chunk_size needs to be divisible by 4 for efficient storage (says Django documentation)
    chunk_size = 5242880 + 1000000

    def __init__(self):
        self.file_sender = None

    def new_file(self, field_name, file_name, content_type, content_length, charset):
        self.file_sender = FileSender(file_name)

    def receive_data_chunk(self, raw_data, start):
        print 'got chunk, start:', start, 'length:', len(raw_data)
        self.file_sender.sendChunk(raw_data)

    def file_complete(self, file_size):
        download_key = self.file_sender.completeUpload(file_size)

        uploaded_file = UploadedFile()
        uploaded_file.download_key = download_key
        uploaded_file.name = self.file_sender.row.filename

        return uploaded_file


