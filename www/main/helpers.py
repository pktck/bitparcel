from boto.s3.connection import S3Connection
from boto.s3.key import Key
import NoDB

AWS_ACCESS_KEY = 'AKIAJNXR4SI3D5DHV5XA'
AWS_SECRET_KEY = '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'
DATA_DIR = '/home/ubuntu/data'


# connection to S3 is made when module is first imported
bucket = S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY).get_bucket('bitparcel')
files_table = NoDB.Manager(DATA_DIR).getDatabase('bitparcel').getTable('files')

class FileGetter(object):
    @classmethod
    def getFile(cls, file_key):
        key_obj = Key(bucket)
        key_obj.key = file_key
        thefile = StringIO.StringIO()
        key_obj.get_file(thefile)
        thefile.seek(0)
        return thefile

    @classmethod
    def getKeyObj(cls, file_key):
        key_obj = Key(bucket)
        key_obj.key = file_key
        return key_obj

    @classmethod
    def getFileKey(cls, download_key):
        row = files_table.getReadOnly(download_key)
        return row.file_key

    @classmethod
    def getRow(cls, download_key):
        row = files_table.getReadOnly(download_key)
        return row


