# from dajax.core import Dajax
from django.utils import simplejson
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_protect
# from dajaxice.decorators import dajaxice_register
# from dajaxice.utils import deserialize_form

from apps.bioface.utils import api_request

# from django.contrib.auth.decorators import login_required
# from django.forms.util import ErrorList
# from django.template.loader import render_to_string

# # from apps.bioface.utils import ajax_login_required
# from apps.bioface.forms import CreateOrganismForm
# from apps.bioface.utils import api_request
# from apps.bioface.views import get_pagination_page

# @dajaxice_register
# # @ajax_login_required
# def pagination(request, page, method, query):
# 	query_dict = {
# 	    "method" : method,
# 	    "key": request.user.sessionkey,
# 	    # "params" : {
# 	    #     # "query" : "reference_id = id",
# 	    #     "limit" : cd['limit'],
# 	    #     "skip" : cd['skip'],
# 	    #     # "orderby" : [["field_name", "acs"], ["field_name2", "desc"]]
# 	    # }
# 	}

# 	template_name, template_context = get_pagination_page(page, query_dict)
# 	render = render_to_string('result_list_paginated.html', template_context)

# 	dajax = Dajax()
# 	dajax.assign('#result-list', 'innerHTML', render)
# 	return dajax.json()

# @dajaxice_register
# def test_span(request):
#     dajax = Dajax()
#     dajax.assign('#test-span', 'innerHTML', 'Hello World!')
#     return dajax.json()

@csrf_protect
def ajax_change_attribute(request):
    if request.method == 'POST':
        # print 2233333, request
        rp = request.POST
        print 44444, rp
        query_dict = {
            "method" : "update_attribute",
            "key": request.user.sessionkey,
            "params" : {
                "id" : int(rp['id']),
                "version": int(rp['version']),
                "operation": rp['operation'],
                "data": simplejson.loads(rp['data'])
            }
        }
        
        content_dict = api_request(query_dict)
            
        if content_dict.has_key('result'):
            results = {
                # 'success': 'success',
                    # 'data': {
                'id': content_dict['result']['id'],
                'version': content_dict['result']['version']
                    # }
            }
        else:
            msg = content_dict['error']['message']
            return HttpResponseBadRequest(msg)

    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')

    
