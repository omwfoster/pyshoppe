from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.api import users

#pinned items contain key references for blob store retrieval
# basic image data for reconstituting blob into URL reference
#


class User(db.Model):
    user_id = db.users.User
    user_name = db.StringProperty


class Pinboard(db.Model):
    name = db.StringProperty()
    owner = db.ReferenceProperty(User)

    def get_contents(self):
        contents_list = self.all().order("-timestamp").fetch(20)

        return contents_list


class Pinned_Item(db.Model):
    pinboard_container = db.ReferenceProperty(Pinboard)

    item_filename = db.StringProperty()
    item_filetype = db.StringProperty()
    content_index = blobstore.BlobReferenceProperty(blobstore.BlobKey,required=False)







    #  def get_blobid_from_filename(filename):

    #    imageblob = db.gql("SELECT content_index WHERE name=:image_name", image_name=filename)
    #    imageblob.get()
    #    assert isinstance(imageblob, object)
    #    return imageblob
