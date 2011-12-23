from boto.s3.connection import S3Connection
from boto.s3.key import Key
import NoDB
from dropbox import client, rest, session
import oauth.oauth as oauth

APP_KEY = 'qrgcb3a3c3vmycf'
APP_SECRET = 'y1ysvtzoisp6fz5'
ACCESS_TYPE = 'app_folder'


#AWS_ACCESS_KEY = 'AKIAJNXR4SI3D5DHV5XA'
#AWS_SECRET_KEY = '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'
DATA_DIR = '/home/ubuntu/data'


# connection to S3 is made when module is first imported
#bucket = S3Connection(AWS_ACCESS_KEY, AWS_SECRET_KEY).get_bucket('bitparcel')
#files_table = NoDB.Manager(DATA_DIR).getDatabase('bitparcel').getTable('files')

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


class DropboxHelper(object):

    @classmethod
    def getRequestTokenAndUrl(cls):
        sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)

        request_token = sess.obtain_request_token()

        url = sess.build_authorize_url(request_token)

        return {'request_token_key': request_token.key,
                'request_token_secret': request_token.secret,
                'url': url}

    @classmethod
    def getAccessToken(cls, request_token_key, request_token_secret):
        sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
        request_token = oauth.OAuthToken(request_token_key, request_token_secret)

        # This will fail if the user didn't visit the above URL and hit 'Allow'
        access_token = sess.obtain_access_token(request_token)

        return {'access_token_key': access_token.key,
                'access_token_secret': access_token.secret}
        



        client = client.DropboxClient(sess)
        print "linked account:", client.account_info()
