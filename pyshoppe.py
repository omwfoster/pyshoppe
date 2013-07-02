import webapp2
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import blobstore_handlers
import os, urllib2
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.api import files
from google.appengine.api import images
from google.appengine.api import channel
from google.appengine.api import users
from imagedb import Pinboard
from imagedb import Pinned_Item


class BaseRequestHandler(webapp2.RequestHandler):
    pinboard = None
    token = None

    def render_template2(self, filename, template_args=None):
        global pinboard
        #@global_blobkey
        user = users.get_current_user()
        pinboard_key = self.request.get('pinboard_key')
        pinboard = None
        if user:
            if not pinboard_key:
                pinboard_key = user.user_id()
                pinboard = Pinboard(name=pinboard_key)
                pinboard.put()
            else:
                pinboard = Pinboard.get_by_key_name(pinboard_key)
                if not pinboard.owner:
                    pinboard.owner = user
                    pinboard.put()

            pinboard_link = 'http://localhost:8080/?pinboard_key=' + pinboard.name

            if pinboard:
                token = channel.create_channel(os.urandom(16).encode('hex'))
                ###token = channel.create_channel(user.user_id() + pinboard)
                template_values = {'token': token,
                                   'me': user.user_id(),
                                   'pinboard_key': pinboard_key
                }

                path = os.path.join(os.path.dirname(__file__), 'templates', filename)
                self.response.out.write(template.render(path, template_values))
            else:
                self.response.out.write('No such game')
        else:
            self.redirect(users.create_login_url(self.request.uri))

    def render_template(self, filename, template_args=None):
        token = channel.create_channel(os.urandom(16).encode('hex'))
        global user_pinboard
        user_pinboard = pinboard(name=token)

        if not template_args:
            template_args = {'token': token, 'pinboard': user_pinboard}

        user_pinboard.put()
        path = os.path.join(os.path.dirname(__file__), 'templates', filename)
        self.response.out.write(template.render(path, template_args))


class startpage(BaseRequestHandler):
    def get(self):
        self.render_template2('index.html', template_args=None)
        self.response.out.write("")

    def post(self):
        self.response.out.write('post request')


class upload(BaseRequestHandler):
    def get(self):
        self.error(403)

    def post(self):
        """


        """


        pinboard_key = self.request.headers['X-pinboard']
        token = self.request.headers['X-token']
        mime_type = self.request.headers['X-File-Type']
        file_name = self.request.headers['X-File-Name']
        blob_name = files.blobstore.create(mime_type=mime_type, _blobinfo_uploaded_filename=file_name)
        with files.open(blob_name, 'a') as f:
            f.write(self.request.body)
        files.finalize(blob_name)
        blobkey = files.blobstore.get_blob_key(blob_name)


        q = Pinboard.gql("WHERE name = :1 ", pinboard_key)
        pinboard = q.get()


        pin1 = Pinned_Item(pinboard_container=pinboard,
                           item_filename=file_name,
                           item_filetype=mime_type,
                           content_index=blobkey)

        pin1.put()
  #      channel.send_message(token, token)

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
    def get(self,file_name=None ):
        #global user_pinboard
        # dummy functionality should instead return a datastore entry
        # prototype will return global_blobstore key
        #

        """

        :param file_name:
        """

        file_name = self.request.get("filename")
        q = Pinned_Item.gql("WHERE item_filename = :1 ", file_name)
        content_index = q.get().content_index.key()
        file_data = blobstore.BlobReader(q.get().content_index.key()).read()
        for item in q:
            file_type = item.item_filetype


        #        if not pin_entry:
        #            self.abort(404)
        self.response.headers['X-File-Type'] = file_type
        self.response.headers['X-File-Type'] = str(file_name)
  #      self.response.headers['X-pinboard'] = self.request.headers['X-pinboard']
  #      self.response.headers['X-token'] =  self.request.headers['X-token']
        self.response.out.write(file_data)# address.content_index)


class pinboardHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):
        """
        return the pinboards contents

        """
        if not blobstore.get(global_blobkey):
            self.error(404)
        else:

        # pinned_items = pinboard.get_contents()
        # for pinned_item in pinned_items:
        #     self.response.out(pinned_item.item_filename)

            #fallback to basic functionality (get something)
            self.send_blob(global_blobkey)


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
    [('/', startpage), ('/upload', upload), ('/canvas', getphotoHandler), ('/pinboard', pinboardHandler)],
    debug=True)

