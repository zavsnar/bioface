from __future__ import unicode_literals

import ast

from dajax.core import Dajax
from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from dajaxice.utils import deserialize_form

from django.forms.util import ErrorList
from django.core.context_processors import csrf
from django.template.loader import render_to_string

from settings import API_URL

from apps.common.forms import CreateOrganismForm
from apps.common.utils import api_request
from apps.common.tasks import loading_objects


@dajaxice_register
def upload_file(request, filename, file_data):
    dajax = Dajax()
    query = {
        "method" : "upload",
        "key": request.user.sessionkey,
        "params" : {
            "data" : {
                "filename": filename, 
                "filetype": "filetype"
                }
            }
        }

    content_dict = api_request(query)

    if content_dict.has_key('result'):
        upload_id = content_dict['result']['upload_id']
        upload_url = '/bioupload/' + upload_id
        dajax.add_data({'upload_url': upload_url, 'upload_id': upload_id}, 'upload_2_server')
    else:
        template_context = {'error_message': 'Query does not exist.'}
        render = render_to_string('components/alert_messages.html', template_context)
        dajax.assign('.extra-message-block', 'innerHTML', render)

    return dajax.json()

@dajaxice_register
def delete_file(request, fileid):
    dajax = Dajax()
    query = {
            "method" : "delete_file",
            "key": request.user.sessionkey,
            "params" : {
                "id" : fileid
        }
    }

    content_dict = api_request(query)

    if content_dict.has_key('result'):
        dajax.add_data(fileid, 'delete_file_from_list')
    else:
        template_context = {'error_message': 'Error: {}'.format(content_dict['error']['message'])}
        render = render_to_string('components/alert_messages.html', template_context)
        dajax.assign('.extra-message-block', 'innerHTML', render)

    return dajax.json()

@dajaxice_register
def add_organism(request, form):
	form = CreateOrganismForm(deserialize_form(form))
	if form.is_valid():
		query_dict = {
			"method" : "add_organism",
			"key": request.user.sessionkey,
			"params" : {
				"data" : {
					"name": form.cleaned_data['name']
				}
			}
		}
	else:
		query_dict = {}

	return add_ajax_form(request = request, form=form, 
		query_dict=query_dict, html_selector='#create_organism')
