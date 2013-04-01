import webapp2
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import blobstore_handlers
import os ,imagedb
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.api import files
from google.appengine.api import images
from google.appengine.api import channel



class BaseRequestHandler(webapp2.RequestHandler):
    def render_template(self, filename, template_args=None):
        token = channel.create_channel(os.urandom(16).encode('hex'))
        if not template_args:
            template_args = {'token': token}

        path = os.path.join(os.path.dirname(__file__), 'templates', filename)
        self.response.out.write(template.render(path, template_args))


class startpage(BaseRequestHandler):
    def get(self):
        self.render_template('index.html',template_args=None)
        self.response.out.write("")

    def post(self):
        self.response.out.write('post request')

class upload(BaseRequestHandler):
    global global_blobkey
    def get(self):
        self.error(403)


    def post(self):
        mime_type = self.request.headers['X-File-Type']
        name = self.request.headers['X-File-Name']
        file_name = files.blobstore.create(mime_type=mime_type,_blobinfo_uploaded_filename=name)

        with files.open(file_name, 'a') as f:
            f.write(self.request.body)

        files.finalize(file_name)
        global_blobkey=files.blobstore.get_blob_key(file_name)
        pinned_item = imagedb.pinned_item(global_blobkey,name,mime_type)
        pinned_item.put()

class ViewPhotoHandler(blobstore_handlers.BlobstoreDownloadHandler):
    global global_blobkey
    def get(self):
#        if not blobstore.get(global_blobkey):
            self.error(404)
        else:
            self.send_blob(global_blobkey)


class pinboardHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):
        """
        return the pinboards contents

        """
        if not blobstore.get(global_blobkey):
            self.error(404)
        else:

#            pinned_items = imagedb.pinboard.get_contents()
#            for pinned_item in pinned_items:
#                self.response.out(pinned_item.item_filename)

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


app = webapp2.WSGIApplication([('/', startpage),('/upload', upload),('/canvas.jpg',ViewPhotoHandler),('/pinboard',pinboardHandler)], debug=True)

