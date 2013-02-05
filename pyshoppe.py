from google.appengine.ext import webapp
from google.appengine.api import images
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
import wsgiref.handlers
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
import os,cgi,sys, urlparse
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.api import files
import urllib


global global_blobkey

class blobImages(db.Model):
    blob = blobstore.BlobReferenceProperty(required=True)


class BaseRequestHandler(webapp.RequestHandler):
    def render_template(self, filename, template_args=None):
        self.response.out.write("base request reached")
        self.response.out.write(template_args)
        if not template_args:
            template_args = {}
    
    
        path = os.path.join(os.path.dirname(__file__), 'templates', filename)
        self.response.out.write(path)
        self.response.out.write(template.render(path, template_args))


class startpage(BaseRequestHandler):
    def get(self):
        self.render_template('index.html',template_args=None)
        self.response.out.write("")

    def post(self):
        self.response.out.write('post request')



class upload(BaseRequestHandler):
    def get(self):
        self.error(403)


    def post(self):
        mime_type = self.request.headers['X-File-Type']
        name = self.request.headers['X-File-Name']
        file_name = files.blobstore.create(mime_type=mime_type,_blobinfo_uploaded_filename=name)

        with files.open(file_name, 'a') as f:
            f.write(self.request.body)

        files.finalize(file_name)
        global global_blobkey
        global_blobkey=files.blobstore.get_blob_key(file_name)


class ViewPhotoHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):
        
        if not blobstore.get(global_blobkey):
            self.error(404)
        else:  
            self.send_blob(global_blobkey)






def main():

    application = webapp.WSGIApplication([('/', startpage),('/upload', upload),('/canvas.jpg',ViewPhotoHandler)], debug=True)

    run_wsgi_app(application)

if __name__ == "__main__":
    main()
