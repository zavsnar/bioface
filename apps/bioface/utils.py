import urllib
import httplib2 
import json

from django.shortcuts import render, render_to_response, redirect

API_URL = 'https://10.0.1.204:5000/api/v1/'

def api_request(query_dict):
    
    headers = {'Content-type': 'application/json'}
    http = httplib2.Http(disable_ssl_certificate_validation=True)

    http_response, content = http.request(API_URL, 'POST', body = json.dumps(query_dict), headers = headers)
    content_dict = json.loads(content)
    if content_dict.has_key('error'):
    	if content_dict['error']['message'] == 'invalid session':
    		return redirect('signin')

    return http_response, content_dict


def ajax_login_required(view_func):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated():
            return view_func(request, *args, **kwargs)

        json = simplejson.dumps({ 'not_authenticated': True })
        return HttpResponse(json, mimetype='application/json')
    wrap.__doc__ = view_func.__doc__
    wrap.__dict__ = view_func.__dict__
    return wrap

def get_choices(request, cache_key='test', key='id', query=None):
	# if cache.has_key(cache_key):
	# 	choices_list = cache.get(cache_key)
	# else:
	# choices_list = (('',''),)
	if cache_key:

		method = 'get_{}'.format(cache_key)
		query_dict = {
            "method" : method,
            "key": request.user.sessionkey,
        }

		if query:
			query_dict['params'] = {}
			query_dict['params']['query'] = query
		http_response, content_dict = api_request(query_dict)

		item_list = content_dict['result'].get(cache_key, [])
		choices_list=[]
		if item_list:
			for item in item_list:
				if item.has_key('name'):
					title = item['name']
				elif item.has_key('tag'):
					title = item['tag']
				choices_list.append((item[key], title))
			# cache.set(cache_key, choices_list, 30)

		# print choices_list
	return choices_list