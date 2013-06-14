from google.appengine.ext import db
from google.appengine.ext import blobstore

#pinned items contain key references for blob store retrieval
# basic image data for reconstituting blob into URL reference
#


class pinboard(db.Model):
    name = db.StringProperty()

    def get_contents(self):
        contents_list = self.all().order("-timestamp").fetch(20)

        return contents_list


class pinned_item(db.Model):
    pinboard_container = db.ReferenceProperty(pinboard)
    item_filename = db.StringProperty()
    item_filetype = db.StringProperty()
    content_index = blobstore.BlobReferenceProperty(blobstore.BlobKey,required=False)





    #  def get_blobid_from_filename(filename):

    #    imageblob = db.gql("SELECT content_index WHERE name=:image_name", image_name=filename)
    #    imageblob.get()
    #    assert isinstance(imageblob, object)
    #    return imageblob
