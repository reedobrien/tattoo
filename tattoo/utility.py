__metaclass__ = type

import datetime
from random import randint

from tattoo.codec import encode
from tattoo.models import URL
from tattoo.codec import BASE
from tattoo.codec import MAX_URL_LEN

MAX_INT = BASE**MAX_URL_LEN

def expire_one_year():
    return datetime.datetime.now()+datetime.timedelta(days=365)

    
class NoURLSupplied(Exception):
    def __str__(self):
        return "No URL was supplied."


class URLAlreadyShorter(Exception):
    def __init__(self, url):
        self.url = url
    def __str__(self):
        return "The URL supplied was shorter than we can make it"


def new_intid():
    uid = randint(0, MAX_INT)
    base_id = encode(uid)
    try:
        URL.m.find({'_id' : uid }).one()
        uid = new_intid()
    except ValueError:
        pass # It doesn't exist; let's use it
    return uid

