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
from imagedb import pinboard
from imagedb import pinned_item


class BaseRequestHandler(webapp2.RequestHandler):
    pinboard

    def __init__(self):
        global pinboard
        user_pinboard = pinboard
        token = 3
        #@global_blobkey
        user = users.get_current_user()
        pinboard = self.request.get('pinboard')

        game = None
        if user:
            if not pinboard:
                pinboard = user_pinboard(pinboard=user.user_id())
                game.put()
            else:

                pinboard = pinboard
                if not game.userO:
                    game.userO = user
                    game.put()

            pinboard_link = 'http://localhost:8080/?pinboard=' + pinboard

            if game:
                token = channel.create_channel(user.user_id() + pinboard)
                template_values = {'token': token,
                                   'me': user.user_id(),
                                   'pinboard': pinboard
                }
                path = os.path.join(os.path.dirname(__file__), 'index.html')

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
            template_args = {'token': token , 'pinboard': user_pinboard}

        user_pinboard.put()
        path = os.path.join(os.path.dirname(__file__), 'templates', filename)
        self.response.out.write(template.render(path, template_args))


class startpage(BaseRequestHandler):
    def get(self):
        self.render_template('index.html', template_args=None)
        self.response.out.write("")

    def post(self):
        self.response.out.write('post request')


class upload(BaseRequestHandler):
    def get(self):
        self.error(403)

    def post(self):
        """


        """

        mime_type = self.request.headers['X-File-Type']
        file_name = self.request.headers['X-File-Name']
        blob_name = files.blobstore.create(mime_type=mime_type, _blobinfo_uploaded_filename=file_name)
        with files.open(blob_name, 'a') as f:
            f.write(self.request.body)
        files.finalize(blob_name)
        global user_pinboard
        global global_blobkey
        global_blobkey = files.blobstore.get_blob_key(blob_name)
        pin1 = pinned_item(pinboard_container=user_pinboard,
                           item_filename=file_name,
                           item_filetype=mime_type,
                           content_index=global_blobkey)

        pin1.put()
        channel.send_message(BaseRequestHandler.token, BaseRequestHandler.token)

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
    def get(self):
        #global user_pinboard
        # dummy functionality should instead return a datastore entry
        # prototype will return global_blobstore key
        #
        file_name = 'imgres.jpg'

        q = pinned_item.gql("WHERE item_filename = :1 ", file_name)
        file_data = blobstore.BlobReader(q.get().content_index.key()).read()

        #        if not pin_entry:
        #            self.abort(404)
        self.response.headers['Content-Type'] = "image/jpg"
        self.response.headers['File-Name'] = file_name
        self.response.out.write(file_data)  #address.content_index)


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

