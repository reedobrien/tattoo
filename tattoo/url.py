import urlparse

from webob.exc import HTTPFound
from webob.exc import HTTPNotFound
from webob.exc import HTTPInternalServerError

from repoze.lru import lru_cache

from repoze.bfg.interfaces import IRoutesMapper
from repoze.bfg.threadlocal import get_current_registry
from repoze.bfg.url import urlencode
from repoze.bfg.settings import get_settings

from tattoo.codec import encode
from tattoo.models import URL
from tattoo.utility import URLAlreadyShorter
from tattoo.utility import NoURLSupplied
from tattoo.utility import new_intid

def route_url(route_name, request, *elements, **kw):
    """
    This is culted from repoze.bfg.url. I just didn't want the path segments (shorturl) percent encoded.
    Read the docstring in repoze.bfg.url for details.
    """
    try:
        reg = request.registry
    except AttributeError:
        reg = get_current_registry() # b/c
    mapper = reg.getUtility(IRoutesMapper)

    anchor = ''
    qs = ''

    if '_query' in kw:
        qs = '?' + urlencode(kw.pop('_query'), doseq=True)

    if '_anchor' in kw:
        anchor = kw.pop('_anchor')
        if isinstance(anchor, unicode):
            anchor = anchor.encode('utf-8')
        anchor = '#' + anchor

    path = mapper.generate(route_name, kw) # raises KeyError if generate fails

    if elements:
        suffix = _join_elements(elements)
        if not path.endswith('/'):
            suffix = '/' + suffix
    else:
        suffix = ''

    return request.application_url + path + suffix + qs + anchor


@lru_cache(1000)
def _join_elements(elements):
    return '/'.join([s for s in elements])


    
class URLTransformer:
    def __init__(self):
        self.settings = get_settings()
        self.min_url_len = int(self.settings['min_url_len'])
        
    def __call__(self, request):
        self.request = request
        self.context = request.context
        self.request_url = self.get_url()
        http_host = self.request.environ['HTTP_HOST'].split(':')[0]
        if self.get_host() == http_host:
            try:
                url = self.context[self.get_path()[1:]].url
                raise HTTPFound(location=url)
            except KeyError:
                raise HTTPNotFound(body="Nobody here but us fish...")
        else:
            if self.too_short(self.request_url):
                raise URLAlreadyShorter(self.request_url)
        result = URL.m.find({'url' : self.request_url})
        count = result.count()
        if count > 1:
            raise HTTPInternalServerError(body='Too many copies of this url in DB already')
        if count == 1:
            existing = result.one()
            raise HTTPFound(location=existing['short_url'])
        else:
            url = self.make_url(self.request_url)

        return url
            
    def get_host(self):
        return urlparse.urlparse(self.request_url).netloc.split(':')[0]

    def get_path(self):
        return urlparse.urlparse(self.request_url).path

    def get_url(self):
        if self.request.method == 'GET':
            data = urlparse.urlsplit(self.request.url).query
        elif self.request.method in ('PUT', 'POST'):
            data = self.request.body
        verify = urlparse.parse_qs(data)
        try:
            url = verify['url'][0]
        except KeyError, IndexError:
            raise NoURLSupplied()
        if not url:
            raise NoURLSupplied()

        return url
    
    def make_url(self, url):
        intid = new_intid()
        short_url = encode(intid)
        model = URL(intid, url, short_url=short_url)
        model.m.save()
        return short_url

    def search_catalog(self, url):
        return self.catalog.search(url={ 'operator' : 'or',
                                         'query': url })

    def too_short(self, url):
        return self.min_url_len > len(url)

url_factory = URLTransformer()
