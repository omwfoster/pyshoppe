from google.appengine.api import images
from google.appengine.ext import blobstore
class imagescrewer():
    blob = blobstore.BlobReferenceProperty(required=True)
    
def invert(blobref):
    
    