"""
Vercel Serverless Entry Point for GNANI VOX Flask Application.
"""

import os
import sys
import json

# Ensure root project directory is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

api_dir = os.path.dirname(__file__)
if api_dir not in sys.path:
    sys.path.insert(0, api_dir)


def _raw_debug_app(environ, start_response):
    """Temporary raw WSGI app to dump all environ keys — bypasses Flask entirely."""
    env_dump = {}
    for k, v in environ.items():
        if isinstance(v, (str, int, float, bool, type(None))):
            env_dump[k] = str(v)[:200]
    
    body = json.dumps({
        'raw_environ': env_dump,
        'REQUEST_METHOD': environ.get('REQUEST_METHOD'),
        'PATH_INFO': environ.get('PATH_INFO'),
        'SCRIPT_NAME': environ.get('SCRIPT_NAME'),
        'QUERY_STRING': environ.get('QUERY_STRING'),
        'SERVER_NAME': environ.get('SERVER_NAME'),
        'HTTP_HOST': environ.get('HTTP_HOST'),
    }, indent=2).encode('utf-8')
    
    start_response('200 OK', [
        ('Content-Type', 'application/json'),
        ('Content-Length', str(len(body))),
    ])
    return [body]


# Check if debug mode is requested via query string
def _is_debug_request(environ):
    qs = environ.get('QUERY_STRING', '')
    return 'gnani_debug=1' in qs


from app import app as _flask_app


def app(environ, start_response):
    """Main WSGI entry point. Routes debug requests to raw handler, rest to Flask."""
    if _is_debug_request(environ):
        return _raw_debug_app(environ, start_response)
    return _flask_app(environ, start_response)
