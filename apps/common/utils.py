import logging
import httplib2 
import json
import csv, codecs, cStringIO

from django.core.cache import cache

from settings import API_URL

logger = logging.getLogger('api_request')

class LoginFailError(Exception):
    pass

# Request to API
def api_request(query_dict):
    headers = {'Content-type': 'application/json'}
    http = httplib2.Http(disable_ssl_certificate_validation=True)
    logger.debug(str(query_dict))
    http_response, content = http.request(API_URL, 'POST', 
        body = json.dumps(query_dict), headers = headers)
    logger.debug(str(content))
    try:
        content_dict = json.loads(content)
        if content_dict.has_key('error'):
            if content_dict['error']['message'] == 'invalid session':
                raise LoginFailError()

    except ValueError:
        content_dict = {
            'error': {
                'message': 'Unknown error',
                'data': 'Unknown error'
            }
        }

    return content_dict


def ajax_login_required(view_func):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated():
            return view_func(request, *args, **kwargs)

        json = simplejson.dumps({ 'not_authenticated': True })
        return HttpResponse(json, mimetype='application/json')
    wrap.__doc__ = view_func.__doc__
    wrap.__dict__ = view_func.__dict__
    return wrap

def get_choices(request, item_name, cache_key='', key='id', query_params='', append_field=''):
    """
        Return list of tuples choices. Format correspond choices in django.forms.ChoiceField.
        If append_field is not empty string, in tuple append that correspond value.
    """

    if not cache_key:
        cache_key = item_name
        
    choices_list = cache.get(cache_key, [])
    
    if choices_list:
        print "CACHE ", cache_key
    else:
        method = 'get_{}'.format(item_name)
        query_dict = {
            "method" : method,
            "key": request.user.sessionkey,
        }

        if query_params:
            query_dict['params'] = query_params
            
        content_dict = api_request(query_dict)
        
        item_list = content_dict['result'].get(item_name, [])
        if item_list:
            for item in item_list:
                title = item['tag'] if item.has_key('tag') else item['name']

                if append_field:
                    append = item[append_field]
                    choices_list.append((item[key], title, append))
                else:
                    choices_list.append((item[key], title))

            cache.set(cache_key, choices_list, 3600)

    return choices_list
