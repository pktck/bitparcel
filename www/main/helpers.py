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


class Helper(object):
    def __init__(self):
       self.conn = S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY)
       self.bucket = self.conn.get_bucket('bitparcel')
       self.table = NoDB.Manager(DATA_DIR).getDatabase('bitparcel').getTable('files')

    def storeFile(self, thefile):
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
        key_obj = Key(self.bucket)
        key_obj.key = file_key
        key_obj.set_contents_from_file(thefile)

        # save local metadata
        row.file_key = file_key
        row.downloads = 0
        row.filename = thefile.name
        row.size = thefile.size
        row.save()

        return download_key

    def getFile(self, file_key):
        key_obj = Key(self.bucket)
        key_obj.key = file_key
        thefile = StringIO.StringIO()
        key_obj.get_file(thefile)
        thefile.seek(0)
        return thefile

    def getFileKey(self, download_key):
        row = table.getReadOnly(download_key)
        return row.file_key

    def getRow(self, download_key):
        row = self.table.getReadOnly(download_key)
        return row

    def generateDownloadKey(self):
        return ''.join([random.choice(string.ascii_letters + string.digits) for i in range(5)])
