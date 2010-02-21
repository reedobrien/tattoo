from repoze.bfg.configuration import Configurator

from ming import Session
from ming.datastore import DataStore

from tattoo.models import populate
from tattoo.models import SESSION_NAME


def setup_db(db_string):
    bind = DataStore(db_string)
    session = Session.by_name(SESSION_NAME)
    session.bind = bind


def app(global_config, setup_db=setup_db, populate=populate, **settings):
    """ This function returns a WSGI application.
    
    It is usually called by the PasteDeploy framework during 
    ``paster serve``.
    """
    db_uri = settings.get('db_path')
    if db_uri is None:
        raise ValueError('db_path must not be None')
    setup_db(db_uri)
    populate()
    config = Configurator(settings=settings)
    config.begin()
    config.add_route(name='home', path='', request_method='GET')
    config.add_route(name='view', path=':short_url', request_method='GET')
    config.add_route(name='post', path ='', request_method='POST')
    config.add_route(name='put', path='', request_method='PUT')
    config.add_route(name='list', path='list', request_method='GET')
    config.add_route(name='nohead', path=':short_url', request_method='HEAD')
    config.add_static_view(name='static', path='templates/static', cache_max_age=0)
    config.scan()
    config.end()
    
    return config.make_wsgi_app()


