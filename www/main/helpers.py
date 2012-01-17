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

class FileExceedsSizeLimit(Exception):
    pass


class BitparcelDownload(object):
    def __init__(self, download_key, file_key, download_session_key, filename):
        self.row = files_table.getRow(download_key, lock_type='exclusive')
        self.download_session_row = download_sessions_table.getRow(download_session_key)

        if self.row.file_key != file_key:
            raise Exception("Download_key and file_key don't match.")
        if self.row.filename != filename:
            raise Exception("Download_key and file_key don't match filename.")

        if self.row.downloads >= 5:
            raise Exception('File has already been downloaded 5 times.')

        self.row.downloads += 1
        self.row.save()
        self.row.releaseLock()

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

    @classmethod
    def getRow(cls, download_key):
        row = files_table.getRow(download_key)
        return row

               
class DownloadSession(object):
    @classmethod
    def create(cls):
        download_session_row = download_sessions_table.createRowWithUniqueKey(5, lock_type='exclusive')
        download_session_row.downloaded_size = 0
        download_session_row.save()
        download_session_row.releaseLock()

        return download_session_row.getKey()

    @classmethod
    def get(cls, download_session_key):
        return download_sessions_table.getRow(download_session_key)
