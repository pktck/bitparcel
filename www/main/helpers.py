from boto.s3.connection import S3Connection
from boto.s3.key import Key
import NoDB
import random
import string
import StringIO
import uuid

AWS_ACCESS_KEY = 'AKIAJNXR4SI3D5DHV5XA'
AWS_SECRET_KEY = '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'
DATA_DIR = '/home/ubuntu/data'


class FileSender(object):
    def __init__(self, row, bucket, file_key, filename):
        self.row = row
        self.mp = bucket.initiate_multipart_upload(file_key)
        self.file_key = file_key
        self.part_counter = 0
        self.filename = filename
        self.data = StringIO.StringIO()

    def addChunk(self, chunk):
        print 'adding chunk'
        self.data.write(chunk)
        if self.data.len >= 5242880:
            self._sendPart()
            self.data.truncate(0)

    def _sendPart(self):
        self.part_counter += 1
        print 'sending part #', self.part_counter
        self.mp.upload_part_from_file(self.data, self.part_counter)

    def completeUpload(self):
        print 'parts:', self.part_counter
        size = sum([part.size for part in self.mp])

        self.mp.complete_upload()

        # save local metadata
        self.row.file_key = self.file_key
        self.row.downloads = 0
        self.row.filename = self.filename
        self.row.size = size
        self.row.save()

        print 'file key:', self.file_key

        return self.row.getKey()


class Helper(object):
    def __init__(self):
       self.conn = S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY)
       self.bucket = self.conn.get_bucket('bitparcel')
       self.table = NoDB.Manager(DATA_DIR).getDatabase('bitparcel').getTable('files')

    def storeFile(self, filename):
        # create a new row
        while True:
            try:
                download_key = self.generateDownloadKey()
                row = self.table.createLocked(download_key)
                break
            except NoDB.RowAlreadyExists:
                continue
    
        file_key = uuid.uuid1().hex

        # store the file on S3
        file_sender = FileSender(row, self.bucket, file_key, filename)

        return file_sender

    def getFile(self, file_key):
        key_obj = Key(self.bucket)
        key_obj.key = file_key
        thefile = StringIO.StringIO()
        key_obj.get_file(thefile)
        thefile.seek(0)
        return thefile

    def getKeyObj(self, file_key):
        key_obj = Key(self.bucket)
        key_obj.key = file_key
        return key_obj

    def getFileKey(self, download_key):
        row = table.getReadOnly(download_key)
        return row.file_key

    def getRow(self, download_key):
        row = self.table.getReadOnly(download_key)
        return row

    def generateDownloadKey(self):
        return ''.join([random.choice(string.ascii_letters + string.digits) for i in range(5)])
