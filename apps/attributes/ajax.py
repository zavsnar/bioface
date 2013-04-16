
from django.utils import simplejson
from django.http import HttpResponse, HttpResponseBadRequest
# from django.views.decorators.csrf import csrf_protect

from apps.bioface.utils import api_request

# @csrf_protect
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

    
