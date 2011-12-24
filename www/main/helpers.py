from boto.s3.connection import S3Connection
from boto.s3.key import Key
import NoDB

AWS_ACCESS_KEY = 'AKIAJNXR4SI3D5DHV5XA'
AWS_SECRET_KEY = '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'
DATA_DIR = '/home/ubuntu/data'


# connection to S3 is made when module is first imported
bucket = S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY).get_bucket('bitparcel')
files_table = NoDB.Manager(DATA_DIR).getDatabase('bitparcel').getTable('files')
download_sessions_table = NoDB.Manager(DATA_DIR).getDatabase('bitparcel').getTable('download_sessions')

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
    def getChunkyKeyObj(cls, file_key, chunk_size=512000):
        key_obj = cls.getKeyObj(file_key)
        while True:
            chunk = key_obj.read(chunk_size)
            if len(chunk) == 0:
                break
            yield chunk

    @classmethod
    def getFileKey(cls, download_key):
        row = files_table.getReadOnly(download_key)
        return row.file_key

    @classmethod
    def getRow(cls, download_key):
        row = files_table.getReadOnly(download_key)
        return row

class BitparcelDownload(object):
    def __init__(self, download_key, file_key, download_session_key, filename):
        self.row = files_table.getReadOnly(download_key)
        self.download_session_row = DownloadSession.get(download_session_key)

        if self.row.file_key != file_key:
            raise Exception("Download_key and file_key don't match.")
        if self.row.filename != filename:
            raise Exception("Download_key and file_key don't match filename.")

    def getChunkyKeyObj(self, chunk_size=512000):
        key_obj = Key(bucket)
        key_obj.key = self.row.file_key
        while True:
            chunk = key_obj.read(chunk_size)
            self.download_session_row.downloaded_size += len(chunk)
            self.download_session_row.save()
            if len(chunk) == 0:
                break
            yield chunk
               
class DownloadSession(object):
    @classmethod
    def create(cls):
        download_session_row = download_sessions_table.createWithUniqueKey(5)
        download_session_row.downloaded_size = 0
        download_session_row.save()

        return download_session_row.getKey()

    @classmethod
    def get(cls, download_session_key):
        return download_sessions_table.get(download_session_key)
