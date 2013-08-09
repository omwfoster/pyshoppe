import os

import webapp2
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore
from google.appengine.api import files
from google.appengine.api import images
from google.appengine.api import channel
from google.appengine.api import users
import StringIO
from contextlib import closing
from zipfile import ZipFile, ZIP_DEFLATED
from StringIO import StringIO

from google.appengine.ext import webapp
from google.appengine.api import urlfetch

from zipfile import ZipFile, ZIP_DEFLATED

from imagedb import Pinboard
from imagedb import Pinned_Item
from imagedb import User

# class xhr_pinboard_zipper():



class BaseRequestHandler(webapp2.RequestHandler):
    pinboard = None
    token = None

    def render_template2(self, filename, template_args=None):
        global pinboard
        #@global_blobkey
        pinboards = Pinboard.all()

        user = users.get_current_user()
        pinboard_url_id = self.request.get('pinboard_url_id')
        pinboard = None
        if user:
            if not pinboard_url_id:
                pinboard_url_id = os.urandom(16).encode('hex')
                pinboard = Pinboard(name=pinboard_url_id, owner=self.createUserentry())
                pinboard.put()
            else:
                pinboard = Pinboard.get_by_key_name(pinboard_url_id)
                pinboard = self.getPinboardfromurlkey(pinboard_url_id)
                if not pinboard.owner:
                    pinboard.owner = self.createUserentry()
                    pinboard.put()

            pinboard_link = 'http://localhost:8080/?pinboard_url_id=' + pinboard.name

            if pinboard:
            ##    token = channel.create_channel(os.urandom(16).encode('hex'))
                ###token = channel.create_channel(user.user_id() + pinboard)
                template_values = {'token': "token",
                                   'me': user.user_id(),
                                   'pinboard_url_id': pinboard_url_id,
                                   'pinboards': pinboards
                }

                path = os.path.join(os.path.dirname(__file__), 'templates', filename)
                self.response.out.write(template.render(path, template_values))
            else:
                self.response.out.write('balls')
        else:
            self.redirect(users.create_login_url(self.request.uri))


    def getPinboardfromurlkey(self, urlPinboardkey):
        q = Pinboard.gql("WHERE name = :1 ", urlPinboardkey)
        pinboard = q.get()
        return pinboard

    def getUserobjectfromID(self):
        q = User.gql("WHERE name = :1 ", users.get_current_user().user_id())
        u = q.get()
        return u


    def createUserentry(self):
        user1 = User(user_id=users.get_current_user().user_id(), name="oliver")
        user1.put()
        return user1


class startpage(BaseRequestHandler):
    def get(self):
        self.render_template2('index.html', template_args=None)

    def post(self):
        self.response.out.write('post request')


class upload(BaseRequestHandler):
    def get(self):
        self.error(403)

    def post(self):
        """


        """

        pinboard_url_id = self.request.headers['X-pinboard']
        token = self.request.headers['X-token']
        mime_type = self.request.headers['X-File-Type']
        file_name = self.request.headers['X-File-Name']
        blob_name = files.blobstore.create(mime_type=mime_type, _blobinfo_uploaded_filename=file_name)
        with files.open(blob_name, 'a') as f:
            f.write(self.request.body)
        files.finalize(blob_name)
        blobkey = files.blobstore.get_blob_key(blob_name)

        q = Pinboard.gql("WHERE name = :1 ", pinboard_url_id)
        pinboard = q.get()

        pin1 = Pinned_Item(pinboard_container=pinboard,
                           item_filename=file_name,
                           item_filetype=mime_type,
                           content_index=blobkey)

        pin1.put()
        channel.send_message(token, 'hOORAH')

    def sendupdateMsg(self):
        """
            send update message using channels api

        """


class viewphotoHandler(blobstore_handlers.BlobstoreDownloadHandler):
    global global_blobkey

    def get(self):
        name = "images.jpg"

        if not blobstore.get(global_blobkey):
            self.error(404)
        else:
            self.send_blob(global_blobkey)


class getphotoHandler(BaseRequestHandler):
    def get(self, file_name=None):

        file_name = self.request.get("filename")
        q = Pinned_Item.gql("WHERE item_filename = :1 ", file_name)
        content_index = q.get().content_index.key()
        file_data = blobstore.BlobReader(q.get().content_index.key()).read()
        for item in q:
            file_type = item.item_filetype

        self.response.headers['X-File-Type'] = str(file_type)
        self.response.headers['X-File-Name'] = str(file_name)
        self.response.out.write(file_data)


class xhr_pinboardHandler(webapp2.RequestHandler):


    def query_for_pinboard(self, url_key):
        q = Pinboard.gql("WHERE name = :1 ", url_key)
        pinboard = q.get()
        return pinboard

    def return_pinboard_contents(self, pinboard):
        q = Pinned_Item.gql("WHERE pinboard_container = :1 ", pinboard)

        return q

    def get(self):


                # Set up headers for browser to correctly recognize ZIP file
        self.response.headers['Content-Type'] = 'application/zip'
        self.response.headers['Content-Disposition'] = \
            'attachment; filename="outfile.zip"'

        pinboard_name = self.request.get("pinboard_url_id")
        pinboard = self.query_for_pinboard(pinboard_name)





        content_collection = self.return_pinboard_contents(pinboard)
        #with closing(ZipFile(StringIO(self.response.out), "w", ZIP_DEFLATED)) as outfile:
        #removed as doesn't work with contextmanager
        f=StringIO()
        file = ZipFile(f, "w")

        for p in content_collection.run():
                file_data = blobstore.BlobReader(p.content_index.key()).read()
                file_type = p.item_filetype
                file_name = p.item_filename
                addResource2(file,file_data,p.item_filename.encode('utf-8'))
        file.close()
        f.seek(0)

        while True:
            buf=f.read(2048)
            if buf=="" : break
            self.response.out.write(buf)

        f.close()

def addResource2(zfile, data, fname):

        # get the contents
        #contents = urlfetch.fetch(url).content
        # write the contents to the zip file
        zfile.writestr(fname, data)



def transform(blob_key):
    img = images.Image(blob_key=global_blobkey)

    #    img.resize(width=32, height=32)
    #    img.horizontal_flip()
    #    thumbnail = img.execute_transforms(output_encoding=images.JPEG)
    #    file_name = files.blobstore.create(mime_type='image/jpeg')#file to write to
    #    blob_key = files.blobstore.get_blob_key(file_name)
    #    with files.open(file_name, 'a') as f:
    #        f.write(thumbnail)
    #
    #    files.finalize(file_name)


app = webapp2.WSGIApplication(
    [('/', startpage), ('/upload', upload), ('/canvas', getphotoHandler), ('/pinboard', xhr_pinboardHandler)],
    debug=True)

