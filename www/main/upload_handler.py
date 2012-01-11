from django.core.files.uploadhandler import FileUploadHandler
from django.core.files.uploadedfile import UploadedFile
from helpers import bucket, files_table
#from NoDB.errors import RowAlreadyExists
#import random
#import string
import uuid
import StringIO


#class FileSender(object):
    #def __init__(self, filename):
        #self.part_counter = 0

        #self.row = files_table.createRowWithUniqueKey(lock_type='exclusive')
        #self.row.file_key = uuid.uuid1().hex
        #self.row.filename = filename
        #self.row.downloads = 0

        #self.mp = bucket.initiate_multipart_upload(self.row.file_key)

    #def sendChunk(self, chunk):
        #self.part_counter += 1
        #chunk_fp = StringIO.StringIO(chunk)
        #self.mp.upload_part_from_file(chunk_fp, self.part_counter)

    #def completeUpload(self, file_size):
        #mp_file_size = sum([part.size for part in self.mp])

        #if file_size != mp_file_size:
            #raise Exception("Uploaded file size doesn't match computed file size.")

        #self.mp.complete_upload()

        ## save local metadata
        #self.row.size = file_size
        #self.row.save()
        #self.row.releaseLock()

        #return self.row.getKey()


class BitparcelUploadHandler(FileUploadHandler):
    # S3 minimum part size plus an extra 1 MB since Django's first chunk is smaller than chunk_size
    # (probably because it subtracts headers from the first chunk)
    # chunk_size needs to be divisible by 4 for efficient storage (says Django documentation)
    chunk_size = 5242880 + 1000000

    def __init__(self):
        self.part_counter = 0

        self.row = files_table.createRowWithUniqueKey(lock_type='exclusive')
        self.row.file_key = uuid.uuid1().hex
        self.row.downloads = 0

        self.mp = bucket.initiate_multipart_upload(self.row.file_key)


    def new_file(self, field_name, file_name, content_type, content_length, charset):
        self.row.filename = file_name

    def receive_data_chunk(self, raw_data, start):
        chunk_fp = StringIO.StringIO(raw_data)
        self.part_counter += 1
        self.mp.upload_part_from_file(chunk_fp, self.part_counter)

    def file_complete(self, file_size):
        mp_file_size = sum([part.size for part in self.mp])

        if file_size != mp_file_size:
            raise Exception("Uploaded file size doesn't match computed file size.")

        self.mp.complete_upload()

        print 'a'

        # save local metadata
        self.row.size = file_size

        print self.row.__dict__

        self.row.save()
        self.row.releaseLock()

        print 'b'

        uploaded_file = UploadedFile()
        print 'c'
        uploaded_file.download_key = self.row.getKey()
        print 'd'
        uploaded_file.name = self.row.filename
        print 'e'
    
        return uploaded_file


