from dajax.core import Dajax
from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from dajaxice.utils import deserialize_form

from django.contrib.auth.decorators import login_required
from django.forms.util import ErrorList
from django.template.loader import render_to_string

# from apps.bioface.utils import ajax_login_required
from apps.bioface.forms import CreateOrganismForm
from apps.bioface.utils import api_request
from apps.bioface.views import get_pagination_page

@dajaxice_register
# @ajax_login_required
def pagination(request, page, method, query):
	query_dict = {
	    "method" : method,
	    "key": request.user.sessionkey,
	    # "params" : {
	    #     # "query" : "reference_id = id",
	    #     "limit" : cd['limit'],
	    #     "skip" : cd['skip'],
	    #     # "orderby" : [["field_name", "acs"], ["field_name2", "desc"]]
	    # }
	}

	template_name, template_context = get_pagination_page(page, query_dict)
	render = render_to_string('result_list_paginated.html', template_context)

	dajax = Dajax()
	dajax.assign('#result-list', 'innerHTML', render)
	return dajax.json()

@dajaxice_register
def test_span(request):
    dajax = Dajax()
    dajax.assign('#test-span', 'innerHTML', 'Hello World!')
    return dajax.json()

