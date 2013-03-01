from dajax.core import Dajax
from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from dajaxice.utils import deserialize_form

from django.contrib.auth.decorators import login_required
from django.forms.util import ErrorList
from django.core.context_processors import csrf
from django.template.loader import render_to_string

# from apps.bioface.utils import ajax_login_required
from apps.bioface.forms import CreateOrganismForm
from apps.bioface.utils import api_request
from forms import ExampleForm

import ast

@dajaxice_register
def assign_test(request):
    dajax = Dajax()
    dajax.assign('#box', 'innerHTML', 'Hello World!')
    dajax.add_css_class('div .alert', 'red')
    return dajax.json()

@dajaxice_register
def multiply(request, a, b):
    dajax = Dajax()
    result = int(a) * int(b)
    dajax.assign('#result','value',str(result))
    return dajax.json()

@dajaxice_register
def sayhello(request):
    return simplejson.dumps({'message':'Hello World'})


@dajaxice_register
def send_form(request, form):
    dajax = Dajax()
    form = ExampleForm(deserialize_form(form))

    if form.is_valid():
        dajax.remove_css_class('#my_form input', 'error')
        dajax.alert("Form is_valid(), your username is: %s" % form.cleaned_data.get('username'))
    else:
        dajax.add_css_class('#my_form input', 'error')
        for error in form.errors:
            dajax.add_css_class('#id_%s' % error, 'error')

    return dajax.json()

@dajaxice_register
def randomize(request):
    dajax = Dajax()
    dajax.assign('#result', 'value', random.randint(1, 10))
    return dajax.json()

def add_ajax_form(request, form, query_dict, html_selector):
	dajax = Dajax()
	if form.is_valid():
		# query_dict = {
		# 	"method" : "add_organism",
		# 	"key": request.user.sessionkey,
		# 	"params" : {
		# 		"data" : {
		# 			"name": form.cleaned_data['name']
		# 		}
		# 	}
		# }

		http_response, content_dict = api_request(query_dict)
		if content_dict.has_key('result'):
			id = content_dict['result']['id']
			name = form.cleaned_data['name']
			dajax.script("success_adding('{0}', '{1}');".format(id, name))
		else:
			form._errors['name'] = ErrorList((content_dict['error']['message'],))
			# error_html = '<span class="help-inline">ERROR: {}</span>'.format(content_dict['error']['data'])
			# dajax.assign('#myModal1 #error_for_name', 'innerHTML', content_dict['error']['message'])
			# dajax.add_css_class('#myModal1 #error_for_name', 'error')
			# dajax.add_css_class('#myModal1 input#id_name', 'error')
	 #        dajax.remove_css_class('#create_organism input', 'error')
	 #        dajax.alert("Form is_valid(), your username is: %s" % form.cleaned_data.get('username'))
	# else:
		# dajax.add_css_class('#create_organism input', 'error')
		# for error in form.errors:
			# dajax.add_css_class('#myModal1 input#id_%s' % error, 'error')

	# render = form
	# dajax.assign('#create_organism', 'innerHTML', render)
	context = {'additional_form': form}
	context.update(csrf(request))
	render = render_to_string('create_organism.html', context)
	dajax.assign(html_selector, 'innerHTML', render)
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

	# dajax = Dajax()
	# form = CreateOrganismForm(deserialize_form(form))
	# if form.is_valid():
	# 	query_dict = {
	# 		"method" : "add_organism",
	# 		"key": request.user.sessionkey,
	# 		"params" : {
	# 			"data" : {
	# 				"name": form.cleaned_data['name']
	# 			}
	# 		}
	# 	}

	# 	http_response, content_dict = api_request(query_dict)
	# 	if content_dict.has_key('result'):
	# 		id = content_dict['result']['id']
	# 		name = form.cleaned_data['name']
	# 		dajax.script("success_adding('{0}', '{1}');".format(id, name))
	# 	else:
	# 		form._errors['name'] = ErrorList((content_dict['error']['message'],))
	# 		# error_html = '<span class="help-inline">ERROR: {}</span>'.format(content_dict['error']['data'])
	# 		# dajax.assign('#myModal1 #error_for_name', 'innerHTML', content_dict['error']['message'])
	# 		# dajax.add_css_class('#myModal1 #error_for_name', 'error')
	# 		# dajax.add_css_class('#myModal1 input#id_name', 'error')
	#  #        dajax.remove_css_class('#create_organism input', 'error')
	#  #        dajax.alert("Form is_valid(), your username is: %s" % form.cleaned_data.get('username'))
	# # else:
	# 	# dajax.add_css_class('#create_organism input', 'error')
	# 	# for error in form.errors:
	# 		# dajax.add_css_class('#myModal1 input#id_%s' % error, 'error')

	# # render = form
	# # dajax.assign('#create_organism', 'innerHTML', render)
	# context = {'add_organism_form': form, 'not_first': True}
	# context.update(csrf(request))
	# render = render_to_string('create_organism.html', context)
	# dajax.assign('#create_organism', 'innerHTML', render)

	# return dajax.json()

# from dajaxwebsite.examples.views import get_pagination_page

# from dajaxice.decorators import dajaxice_register

# from django.core.paginator import Paginator, InvalidPage, EmptyPage

# def get_pagination_page(page=1):
#     items = range(0, 100)
#     paginator = Paginator(items, 10)
#     try:
#         page = int(page)
#     except ValueError:
#         page = 1

#     try:
#         items = paginator.page(page)
#     except (EmptyPage, InvalidPage):
#         items = paginator.page(paginator.num_pages)

#     return items

from apps.bioface.views import get_pagination_page

@dajaxice_register
# @ajax_login_required
def pagination(request, page, method, query):
	query_dict = ast.literal_eval(query)
	print query_dict
	raise
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

