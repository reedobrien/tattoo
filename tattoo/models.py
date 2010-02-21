__metaclass__ = type

import datetime

from repoze.bfg.security import Allow
from repoze.bfg.security import Everyone
from repoze.bfg.security import Authenticated

from ming import Document
from ming import Field
from ming import Session
from ming import schema

SESSION_NAME = 'urls'


class URL(Document):
    __acl__ = [ (Allow, Everyone, 'view'),
                (Allow, Authenticated, 'manage') ]
    
    class __mongometa__:
        session = Session.by_name(SESSION_NAME)
        name = 'url'

    _id = Field(schema.Int)
    url = Field(str)
    short_url = Field(str)
    created = Field(schema.DateTime)


    def __init__(self, intid, url, short_url=None):
        self._id = intid
        self.url = url
        self.short_url = short_url
        self.created = datetime.datetime.now()


def populate():
    try:
        model = URL.m.find({'short_url' : u'koan'}).next()   
    except StopIteration:
        model = URL(intid=9376708, short_url=u'koan', url=u'http://koansys.com/')
        model.m.save()
        model = URL(intid=11413773, short_url=u'docs', url=u'http://docs.repoze.org/docs/')
        model.m.save()
 
