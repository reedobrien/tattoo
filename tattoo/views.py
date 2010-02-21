from webob import Response
from webob.exc import HTTPCreated
from webob.exc import HTTPFound
from webob.exc import HTTPMethodNotAllowed
from webob.exc import HTTPNotFound
from webob.exc import HTTPPreconditionFailed
from webob.exc import HTTPSeeOther

from repoze.bfg.settings import get_settings
from repoze.bfg.view import bfg_view

from tattoo.models import URL
from tattoo.url import route_url
from tattoo.url import url_factory
from tattoo.utility import NoURLSupplied
from tattoo.utility import URLAlreadyShorter
from tattoo.utility import expire_one_year


@bfg_view(route_name="home", renderer="templates/main.pt")
def home_view(request):
    settings = get_settings()
    return { 'title' : settings['title'],
             'description': settings['description'],
             'app_url' : request.application_url,
             }

@bfg_view(route_name='view')
def url_view(request, URL=URL):
    """model for test hooks"""
    matchdict = request.matchdict
    try:
        context = URL.m.find({'short_url' : matchdict['short_url']}).one()
        resp = HTTPFound(location=context.url)
        resp.expires=expire_one_year()
    except StopIteration:
        resp = HTTPNotFound(body="<h1>404 Not Found</h1> Nobody here but us fish...glug glug.")
    return resp
        
@bfg_view(route_name='post')
def create_post_view(request, url_factory=url_factory):
    """url_factory arg only for testing purposes"""
    ## TODO: Factor me!!
    try:
        url = url_factory(request)
        response = Response(content_type='text/plain',
                            body=route_url('post', request, url))
    except NoURLSupplied:
        ## TODO: verify this is the right HTTP response.
        return HTTPPreconditionFailed("no url was supplied")
    except (HTTPNotFound, HTTPPreconditionFailed), e:
        return e
    except URLAlreadyShorter, e:
        response = HTTPSeeOther(location=e.url)
    except HTTPFound, e:
        response = HTTPSeeOther(location=route_url('put', request, e.location))

    return response


@bfg_view(route_name='put')
def put_view(request, url_factory=url_factory):
    """Once again url_factory is only here for hooking in tests"""
    ## TODO: Factor me!!
    try:
        url = url_factory(request)
        location = route_url('put', request, url)
        response = HTTPCreated(location=location)
    except NoURLSupplied:
        ## TODO: verify this is the right HTTP response.
        response = HTTPPreconditionFailed("no url was supplied")
    except (HTTPNotFound, HTTPPreconditionFailed), e:
        response = e
    except URLAlreadyShorter, e:
        response = HTTPSeeOther(location = e.url)
    except HTTPFound, e:
        response = HTTPSeeOther(location=route_url('put', request, e.location))
                                
    return response


# @bfg_view(route_name='list')
# def catalog_list_view(request, ):
#     results_data = URL.m.find()
    
#     body= '\n'.join((route_url('view',
#                                request,
#                                x['short_url']) for x in results_data))
#     response = Response(content_type='text/plain',
#                         body=body)
#     return response


@bfg_view(route_name='nohead')
def not_allowed(request):
    return HTTPMethodNotAllowed(allow = "GET")

