from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.api import images
from google.appengine.api import users


#pinned items contain key references for blob store retrieval
# basic image data for reconstituting blob into URL reference
#




class pinned_item(db.Model):

    def __init__(self,content_index,item_filetype,item_filename):
        self.content_index = content_index
        self.item_filename = item_filename
        self.item_filetype = item_filetype



class pinboard(db.model):
    contents = db.ReferenceProperty(pinned_item,
        collection_name='pinboard_contents')

    def get_contents(self):
        contents_list = db.GqlQuery("SELECT * "
                                    "FROM pinboard_contents")

        return contents_list

