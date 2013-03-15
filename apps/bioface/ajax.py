import ast
import csv
from multiprocessing import Process

from dajax.core import Dajax
from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from dajaxice.utils import deserialize_form

from django.contrib.auth.decorators import login_required
from django.forms.util import ErrorList
from django.core.context_processors import csrf
from django.template.loader import render_to_string
from django.core.files import File

from settings import MEDIA_ROOT

# from apps.bioface.utils import ajax_login_required
from apps.bioface.forms import CreateOrganismForm, DownloadForm
from apps.bioface.utils import api_request
from apps.bioface.models import SavedQuery, Download


def prepair_objects(query_dict, object_download):
    content_dict = api_request(query_dict)
    print content_dict
    if content_dict.has_key('result'):
        print 88888, content_dict['result']['objects'][:2]
        objects = content_dict['result']['objects']
        file_name = 'download_id_{}.csv'.format(object_download.id)
        file_path = MEDIA_ROOT + file_name
        print 7777, file_path
        with open(file_path, 'wb') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=str(','), quotechar=str('|'), quoting=csv.QUOTE_MINIMAL)
            col_list = []
            attr_col_list = []
            for key, val in objects[0].iteritems():
                if key == 'attributes':
                    attr_col_list = [ attr['name'] for attr in val ]
                else:
                    col_list.append(key)
            col_list.extend(attr_col_list)

            # spamwriter.writerow([ key for key, val in objects[0].iteritems() ])
            spamwriter.writerow(col_list)
            for obj in objects:
                obj_vals = []
                obj_attrs_val = [ None for i in attr_col_list ]
                for key, val in obj.iteritems():
                    if key == 'attributes':
                        for attr in val:
                            idx = attr_col_list.index(attr['name'])
                            obj_attrs_val[idx] = attr['value']
                    else:
                        obj_vals.append(val)
                obj_vals.extend(obj_attrs_val)
                try:
                    spamwriter.writerow(obj_vals)
                except UnicodeEncodeError:
                    print 666666, obj_vals

        with open(file_path, 'rb') as csvfile:
            object_download.status = 'complete'
            object_download.file_path.save(file_name, File(csvfile), save=False)
            object_download.save(update_fields=('status', 'file_path'))

    return True

@dajaxice_register
def download_objects(request, form, query_dict):
    query_dict = ast.literal_eval(query_dict)
    form_data = deserialize_form(form)
    form = DownloadForm(data = form_data)
    if form.is_valid():
        del query_dict['params']['limit']
        del query_dict['params']['skip']
        # thread = Process(target = prepair_objects, kwargs = {'query_dict': query_dict})
        
        # thread = threading.Thread(target = daemon_test)
        # thread.daemon = True
        object_download = Download.objects.create(
            # encoding = form.cleaned_data['encoding'],
            user = request.user,
            description = form.cleaned_data['description'],
            status = 'expected')

        thread = Process(target = prepair_objects, args = (query_dict, object_download))
        thread.start()
        msg = 'Ok'
    else:
        msg = 'err'
    
    dajax = Dajax()
    # dajax.assign('#js_object_result_table', 'innerHTML', render)
    # dajax.script('stop_show_loading();')
    # dajax.alert(msg)
    return dajax.json()

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
    
import random
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

		content_dict = api_request(query_dict)
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

