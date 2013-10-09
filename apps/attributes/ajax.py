
from django.utils import simplejson
from django.http import HttpResponse, HttpResponseBadRequest

from apps.common.utils import api_request

def ajax_change_attribute(request):
    if request.method == 'POST':
        rp = request.POST
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
                'id': content_dict['result']['id'],
                'version': content_dict['result']['version']
            }
        else:
            msg = content_dict['error']['message']
            return HttpResponseBadRequest(msg)

    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')

    
