#-*- encoding: utf-8 -*-
__metaclass__ = type

import datetime
import unittest

from repoze.bfg.configuration import Configurator
from repoze.bfg import testing

        
document = { '_id': 87299402996L,
             'created': datetime.datetime(2010, 2, 23, 16, 13, 30, 313000),
             'short_url': u'8K!kpD',
             'url': u'AUrl'
             }

class DummyCursor:
    def one(self):
        try:
            raise self.__dict__['test_stop_iteration']
        except KeyError:
            return ModelURL(self.document)

class DummyURL:
    def __init__(self, **kwargs):
        self.m = DummySessionManager()
        self.m.__dict__ = self.__dict__

        
class DummySessionManager:
    def find(self, nada):
        import datetime
        cursor = DummyCursor()
        cursor.__dict__ = self.__dict__
        cursor.document = document

        return cursor


class ModelURL:
    def __init__(self, arg):
        for k,v in arg.items():
            setattr(self, k, v)

    def __call__(self, arg):
        raise StopIteration
            
            
URL = DummyURL()

class mock_transformer:
    """Dummy URL Transformer/Factory"""
    def __init__(self):
        import webob.exc as wo
        from tattoo.utility import NoURLSupplied
        from tattoo.utility import URLAlreadyShorter
        self.settings = {
            'title' : 'Tattoo', 
            'description' : 'Another URL Shortener',
            'min_url_len': '21',
            'reload_templates' : False
            }
        self.__dict__ = {
            "test_zero" : NoURLSupplied("dummy"),
            "test_one" : wo.HTTPFound(location='dummy'),
            "test_not_found": wo.HTTPNotFound("dummy"),
            "test_precondfailed" : wo.HTTPPreconditionFailed("dummy"),
            "test_too_short" : URLAlreadyShorter("short"),
            }
    def __call__(self, arg):
        if hasattr(arg, 'dispatch'):
            resp = self.__dict__[arg.dispatch]
            raise resp
        return 'shorturl'
        
        
url_factory = mock_transformer()

class ViewTests(unittest.TestCase):

    """ These tests are unit tests for the view.  They test the
    functionality of *only* the view.  They register and use dummy
    implementations of repoze.bfg functionality to allow you to avoid
    testing 'too much'"""

    def setUp(self):
        """ cleanUp() is required to clear out the application registry
        between tests (done in setUp for good measure too)
        """
        self.config = Configurator()
        self.config.begin()
        self.config.add_settings({'title' : 'Tattoo', 'description' : 'Another URL Shortener'})
        self.config.add_route(name='home', path='', request_method='GET')
        self.config.add_route(name='view', path=':short_url', request_method='GET')
        self.config.add_route(name='post', path ='', request_method='POST')
        self.config.add_route(name='put', path='', request_method='PUT')
        self.config.add_route(name='list', path='list', request_method='GET')
        self.config.add_route(name='nohead', path=':short_url', request_method='HEAD')
        self.config.add_static_view(name='static', path='templates/static', cache_max_age=0)
        self.config.scan()
        
    def tearDown(self):
        """ cleanUp() is required to clear out the application registry
        between tests
        """
        self.config.end()

    def _callFUT(self, context, request, view):
        return view(request)

    def test_home_view(self):
        from tattoo.views import home_view
        context = testing.DummyModel(title='Tattoo',
                                     description="URL Shortener")
        request = testing.DummyRequest()
        self._callFUT(context, request, home_view)
        view = home_view(request)
        self.assertEquals(view['title'], 'Tattoo')
        self.assertEquals(view['description'], "Another URL Shortener")

    
class ViewIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.config = Configurator()
        self.config.begin()
        self.config.add_settings({'title' : 'Tattoo', 
                                  'description' : 'Another URL Shortener',
                                  'min_url_len': '21',
                                  'reload_templates' : False})
        self.config.add_route(name='home', path='', request_method='GET')
        self.config.add_route(name='view', path=':short_url', request_method='GET')
        self.config.add_route(name='post', path ='', request_method='POST')
        self.config.add_route(name='put', path='', request_method='PUT')
        self.config.add_route(name='list', path='list', request_method='GET')
        self.config.add_route(name='nohead', path=':short_url', request_method='HEAD')
        self.config.add_static_view(name='static', path='templates/static', cache_max_age=0)
        self.config.scan()

    def tearDown(self):
         self.config.end()

    def _make_request(self, dispatch):
        request = testing.DummyRequest(              
            url='AURL',
            environ={'HTTP_HOST': 'bfg.io:80'},
            matchdict= {'short_url': u'8K!kpD'},
            dispatch=dispatch)
        return request

    def test_url_view(self):
        from tattoo.views import url_view
        request = self._make_request(dispatch=None)
        result = url_view(request, URL=URL)
        self.assertEquals(result.status, '302 Found')
        self.assertEquals(result.headers['location'], 'AUrl')

    def test_url_not_found(self):
        from tattoo.views import url_view
        request = self._make_request(dispatch='test_stop_iteration')
        URL = DummyURL()
        URL.m.find = ModelURL({})
        URL.m.find.one = StopIteration
        result = url_view(request, URL=URL)
        self.assertEquals(result.status, '404 Not Found')
        self.assertEquals(result.body, '<h1>404 Not Found</h1> Nobody here but us fish...glug glug.')
        

    def test_post_view_new(self):
        from tattoo.views import create_post_view
        request = testing.DummyRequest(              
            url='http://bfg.io/create?url=http://example.com/somplace/really/long',
            environ={'HTTP_HOST': 'bfg.io:80'})
        result = create_post_view(request, url_factory=url_factory)
        self.assertEqual(result.status, '200 OK')

    def test_post_view_zero(self):
        from tattoo.views import create_post_view
        request = self._make_request(dispatch='test_zero')
        result = create_post_view(request, url_factory=url_factory)
        self.assertEqual(result.status, '412 Precondition Failed')

    def test_post_view_one(self):
        from tattoo.views import create_post_view
        request = self._make_request(dispatch='test_one')
        result = create_post_view(request, url_factory=url_factory)
        self.assertEqual(result.status, '303 See Other')

    def test_post_view_not_found(self):
        from tattoo.views import create_post_view
        request = self._make_request(dispatch='test_not_found')
        result = create_post_view(request, url_factory=url_factory)
        self.assertEqual(result.status, '404 Not Found')

    def test_post_view_precond_failed(self):
        from tattoo.views import create_post_view
        request = self._make_request(dispatch='test_precondfailed')
        result = create_post_view(request, url_factory=url_factory)
        self.assertEqual(result.status, '412 Precondition Failed')
        
    def test_post_view_too_short(self):
        from tattoo.views import create_post_view
        request = self._make_request(dispatch='test_too_short')
        result = create_post_view(request, url_factory=url_factory)
        self.assertEqual(result.status, '303 See Other')
        self.assertEqual(result.headers['location'], 'short')

    def test_put_view_integration(self):
        from tattoo.views import put_view
        request = testing.DummyRequest(              
            url='http://bfg.io/create?url=http://example.com/somplace/really/long',
            environ={'HTTP_HOST': 'bfg.io:80'})
        result = put_view(request, url_factory=url_factory)
        self.assertEqual(result.status, '201 Created')

    def test_put_view_zero(self):
        from tattoo.views import put_view
        request = self._make_request(dispatch='test_zero')
        result = put_view(request, url_factory=url_factory)
        self.assertEqual(result.status, '412 Precondition Failed')

    def test_put_view_one(self):
        from tattoo.views import put_view
        request = self._make_request(dispatch='test_one')
        result = put_view(request, url_factory=url_factory)
        self.assertEqual(result.status, '303 See Other')

    def test_put_view_not_found(self):
        from tattoo.views import put_view
        request = self._make_request(dispatch='test_not_found')
        result = put_view(request, url_factory=url_factory)
        self.assertEqual(result.status, '404 Not Found')

    def test_put_view_precond_failed(self):
        from tattoo.views import put_view
        request = self._make_request(dispatch='test_precondfailed')
        result = put_view(request, url_factory=url_factory)
        self.assertEqual(result.status, '412 Precondition Failed')
        
    def test_put_view_too_short(self):
        from tattoo.views import put_view
        request = self._make_request(dispatch='test_too_short')
        result = put_view(request, url_factory=url_factory)
        self.assertEqual(result.status, '303 See Other')
        self.assertEqual(result.headers['location'], 'short')

    def test_not_allowed(self):
        from tattoo.views import not_allowed
        request = self._make_request(dispatch=None)
        result = not_allowed(request)
        self.assertEquals(result.status, '405 Method Not Allowed')
        self.assertEquals(result.headers['Allow'], 'GET') 


class CodecTests(unittest.TestCase):
    def setUp(self):
        self.config = Configurator()
        self.config.begin()
    
    def tearDown(self):
        self.config.end()

    def _make_codec(self):
        from tattoo.codec import decode, encode, map_dict
        CHARS = u"ABC123.ä~€+"
        BASE = len(CHARS)
        map_dict.clear()
        for num in range(BASE):
            map_dict[num] = CHARS[num]
            map_dict[CHARS[num]] = num
        return decode, encode, map_dict

    def test_encode(self):
        decode, encode, map_dict = self._make_codec()
        self.assertEqual(encode(0), u'A')
        self.assertEqual(encode(10), u'+')
        self.assertEqual(encode(7), u'\xe4')
        self.assertEqual(encode(4), u'2')

    def test_decode(self):
        decode, encode, map_dict = self._make_codec()
        self.assertEqual(decode(u'A'), 0)
        self.assertEqual(decode(u'+'), 10)
        self.assertEqual(decode(u'\xe4'), 7)
        self.assertEqual(decode(u'2'), 4)

class ModelTests(unittest.TestCase):
    def setUp(self):
        self.config = Configurator()
        self.config.begin()
    
    def tearDown(self):
        self.config.end()

    def test_url_model(self):
        from tattoo.models import URL
        url = URL(1234, 'long', 'short')
        self.assertEquals(url._id, 1234)
        self.assertEquals(url.url, 'long')
        self.assertEquals(url.short_url, 'short')
        self.assertEquals(type(url.created), type(datetime.datetime.now()))


def setup_db(db_string):
    return True

def populate():
    return True

class TestRun(unittest.TestCase):
    def setUp(self):
        self.config = Configurator()
        self.config.begin()
        
    def tearDown(self):
        self.config.end()

    def test_app(self):
        from tattoo.run import app
        myapp = app(None, 
                    setup_db=setup_db, 
                    populate=populate, 
                    db_path='mongo://foo.com:1235/dbname',
                    min_url_len=21,
                    )
        self.assertEquals(myapp.__class__.__name__, 'Router')
        
    def test_app_without_db_string(self):
        from tattoo.run import app
        self.assertRaises(ValueError, app, 
                          None, 
                          setup_db=setup_db, 
                          populate=populate, 
                          min_url_len=21,
                          )

    def test_setup_db(self):
        from tattoo.run import setup_db
        from ming import Session
        from tattoo.models import SESSION_NAME
        db_uri = 'mongo://foo.com:1235/dbname'
        setup_db(db_uri)
        session = Session.by_name(SESSION_NAME)
        self.assertTrue(SESSION_NAME in session._registry.keys())

class TestUtility(unittest.TestCase):
    def setUp(self):
        self.config = Configurator()
        self.config.begin()
        
    def tearDown(self):
        self.config.end()

    def test_expire_one_year(self):
        import datetime
        from tattoo.utility import expire_one_year
        nowish = datetime.datetime.now()
        delta = expire_one_year()-nowish
        self.assertEquals(delta.days, 365)

