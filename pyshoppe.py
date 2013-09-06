import os
import webapp2
import StringIO
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore
from google.appengine.api import files
from google.appengine.api import images
from google.appengine.api import channel
from google.appengine.api import users
from StringIO import StringIO
from zipfile import ZipFile, ZIP_DEFLATED
from imagedb import Pinboard
from imagedb import Pinned_Item
from imagedb import User





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
            if pinboard_url_id:
                pinboard = self.getPinboardfromurlkey(pinboard_url_id)
                if not pinboard.owner:
                    pinboard.owner = self.createUserentry()
                    pinboard.put()

            else:
                pinboard = self.locateUserPinboard()
                if not pinboard:
                    pinboard = self.createUserPinboard()
            pinboard_url_id = pinboard.name


            if pinboard:
                token = channel.create_channel(os.urandom(16).encode('hex'))
                # token = channel.create_channel(user.user_id() + pinboard)
                pinboards = Pinboard.all()
                template_values = {'token': token,
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

    def getMask(self):
        return

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

    def locateUserPinboard(self):
        q = Pinboard.gql("WHERE owner = :1 ",
                         User.gql("WHERE user_id =:1", users.get_current_user().user_id()).get()).get()
        return q

    def createUserPinboard(self):
        Pin1 = Pinboard(name=(os.urandom(16).encode('hex')), owner=self.createUserentry())
        Pin1.put()
        return Pin1


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
        size = 200, 200
        file_name = self.request.get("filename")
        q = Pinned_Item.gql("WHERE item_filename = :1 ", file_name)
        content_index = q.get().content_index.key()
        file_data = blobstore.BlobReader(q.get().content_index.key()).read()
        for item in q:
            file_type = item.item_filetype

        self.response.headers['X-File-Type'] = str(file_type)
        self.response.headers['X-File-Name'] = str(file_name)
        self.response.out.write(makeThumb(file_data, (110, 105), str(file_name)))


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
        f = StringIO()
        file = ZipFile(f, "w")

        for p in content_collection.run():
            file_data = blobstore.BlobReader(p.content_index.key()).read()
            file_type = p.item_filetype
            file_name = p.item_filename
            addResource2(file, makeThumb(file_data, (110, 105), p.item_filename.encode('utf-8')),
                         p.item_filename.encode('utf-8'))
        file.close()
        f.seek(0)

        while True:
            buf = f.read(2048)
            if buf == "": break
            self.response.out.write(buf)


def makeThumb(imgblob, size, filename):
    """
    The input image is cropped and then resized by PILs thumbnail method.
    """

    img = images.Image(imgblob)
    path = os.path.join(os.path.dirname(__file__), 'balls', 'polaroid_resize.jpg')

    cropped_img = cropit(img, size)

    #cropped_img.thumbnail(size, Image.ANTIALIAS)
    #return cropped_img

    img.resize(width=118, height=107)
    #  img.vertical_flip()
    thumbnail = img.execute_transforms(output_encoding=images.PNG)

    composite = images.composite(
        [(images.Image(file(path, 'rb').read()), 0, 0, 1.0, images.TOP_LEFT),
         (thumbnail, 5,10, 1.0, images.TOP_LEFT)], 120,
        145)

    return composite


def addResource2(zfile, data, fname):
    # get the contents
    #contents = urlfetch.fetch(url).content
    # write the contents to the zip file
    zfile.writestr(fname, data)


def boxParamsCenter(width, height):
    """
    Calculate the box parameters for cropping the center of an image based
    on the image width and image height
    """
    if  isLandscape(width, height):
        left_x = float(0)
        top_y = ((width - height)/(2 * float(width)))
        right_x = float(1)
        bottom_y = (1 - ((width - height)/(2 * float(width))))
        return left_x, top_y, right_x, bottom_y
    else:
        left_x = (1 - ((height - width)/(2 * float(height))))
        top_y = float(0)
        right_x = ((height - width)/(2 * float(height)))
        bottom_y = float(1)
        return left_x, top_y, right_x, bottom_y


def isLandscape(width, height):
    """
    Takes the image width and height and returns if the image is in landscape
    or portrait mode.
    """
    if width >= height:
        return True
    else:
        return False


def cropit(img, size):
    """
    Performs the cropping of the input image to generate a square thumbnail.
    It calculates the box parameters required by the PIL cropping method, crops
    the input image and returns the cropped square.
    """
    img_width, img_height = size
    left_x, top_y, right_x, bottom_y = boxParamsCenter(img.width, img.height)
    region = img.crop(top_y, left_x, bottom_y, right_x)
    return region




app = webapp2.WSGIApplication(
    [('/', startpage), ('/upload', upload), ('/canvas', getphotoHandler), ('/pinboard', xhr_pinboardHandler)],
    debug=True)

