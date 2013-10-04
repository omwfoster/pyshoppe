from google.appengine.ext import db
from google.appengine.ext import blobstore
import json
from google.appengine.api import users

#pinned items contain key references for blob store retrieval
# basic image data for reconstituting blob into URL reference
#


class User(db.Model):
    user_id = db.StringProperty()
    user_name = db.StringProperty()


class Pinboard(db.Model):
    name = db.StringProperty()
    owner = db.ReferenceProperty(User)

    def get_contents(self):
        contents_list = self.all().order("-timestamp").fetch(20)

        return contents_list

    def get_json(self):
        q = Pinned_Item.gql("WHERE pinboard_container = :1", self)

        json_pinboard = []

        for item in q:
            record = {"item_xpos": item.item_xpos, "item_ypos": item.item_ypos, "UID": item.item_UID}
            json_pinboard.append(record)

        return json.dumps(json_pinboard)



class User_Session(db.Model):
    user = db.ReferenceProperty(User)
    user_pinboard = db.ReferenceProperty(Pinboard)
    token = db.StringProperty()


class Pinned_Item(db.Model):
    pinboard_container = db.ReferenceProperty(Pinboard)
    item_UID = db.StringProperty()
    item_filename = db.StringProperty()
    item_filetype = db.StringProperty()
    item_xpos = db.IntegerProperty()
    item_ypos = db.IntegerProperty()
    content_index = blobstore.BlobReferenceProperty(blobstore.BlobKey, required=False)







    #  def get_blobid_from_filename(filename):

    #    imageblob = db.gql("SELECT content_index WHERE name=:image_name", image_name=filename)
    #    imageblob.get()
    #    assert isinstance(imageblob, object)
    #    return imageblob
