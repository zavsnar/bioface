import urllib
import httplib2 
import json

from django.shortcuts import render, render_to_response, redirect

def api_request(query_dict):
    API_URL = 'https://10.0.1.204:5000/api/v1/'
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