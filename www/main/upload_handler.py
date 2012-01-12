from django.core.files.uploadhandler import FileUploadHandler
from django.core.files.uploadedfile import UploadedFile
from helpers import bucket, files_table, FileExceedsSizeLimit
import uuid
import StringIO


class BitparcelUploadHandler(FileUploadHandler):
    # S3 minimum part size plus an extra 1 MB since Django's first chunk is smaller than chunk_size
    # (probably because it subtracts headers from the first chunk)
    # chunk_size needs to be divisible by 4 for efficient storage (says Django documentation)
    chunk_size = 5242880 + 1000000
    max_file_size = 2 * (2**30)

    def __init__(self):
        self.part_counter = 0

        self.row = files_table.createRowWithUniqueKey(lock_type='exclusive')
        self.row.file_key = uuid.uuid1().hex
        self.row.downloads = 0

        self.mp = bucket.initiate_multipart_upload(self.row.file_key)

    def new_file(self, field_name, file_name, content_type, content_length, charset):
        if content_length > self.max_file_size:
            raise FileExceedsSizeLimit

        self.row.filename = file_name

    def receive_data_chunk(self, raw_data, start):
        chunk_fp = StringIO.StringIO(raw_data)
        self.part_counter += 1
        self.mp.upload_part_from_file(chunk_fp, self.part_counter)

        mp_file_size = sum([part.size for part in self.mp])

        if mp_file_size > self.max_file_size:
            raise FileExceedsSizeLimit

    def file_complete(self, file_size):
        mp_file_size = sum([part.size for part in self.mp])

        if file_size > self.max_file_size or mp_file_size > self.max_file_size:
            raise FileExceedsSizeLimit

        if file_size != mp_file_size:
            raise Exception("Uploaded file size doesn't match computed file size.")

        self.mp.complete_upload()

        # save local metadata
        self.row.size = file_size
        self.row.save()
        self.row.releaseLock()

        uploaded_file = UploadedFile()
        uploaded_file.download_key = self.row.getKey()
        uploaded_file.name = self.row.filename
    
        return uploaded_file


