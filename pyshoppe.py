from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
import wsgiref.handlers
import os


class BaseRequestHandler(webapp.RequestHandler):
    def render_template(self, filename, template_args=None):
        self.response.out.write("base request reached")
        self.response.out.write(template_args)
        if not template_args:
            template_args = {}
    
    
        path = os.path.join(os.path.dirname(__file__), 'templates', filename)
        self.response.out.write(path)
        self.response.out.write(template.render(path, template_args))


class upload(BaseRequestHandler):
    def get(self):
        self.render_template('index.html',template_args=None)
        self.response.out.write("")
    def post(self):
#     files = self.request.POST.multi.__dict__['_items']
        self.response.out.write('post request')
#     for file in files:
#         file=file[1]
#        obj = Download_file(data=file.value, mimetype=file.type)
#        obj.put()
#        file_url = "http://%s/download/%d/%s" % (self.request.host, obj.key().id(), file.filename)

#       file_url = "<a href='%s'>%s</a>" % (file_url,file_url,)
#         obj.download_url=file_url
#         obj.put()
#         self.response.out.write("Your uploaded file is now available at %s </br>" % (file_url))



application = webapp.WSGIApplication([('/', upload)], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
