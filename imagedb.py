from google.appengine.ext import db
from google.appengine.ext import blobstore


#pinned items contain key references for blob store retrieval
# basic image data for reconstituting blob into URL reference
#

class pinned_item(db.Model):
        content_index = db.BlobKey
        item_filename = db.StringProperty()
        item_filetype = db.StringProperty()

class pinboard(db.Model):

    contents = db.ReferenceProperty(pinned_item,collection_name='pinboard_contents')

    def get_contents(self):
        contents_list = db.GqlQuery("SELECT *"
                                    "FROM pinboard")

        return contents_list

