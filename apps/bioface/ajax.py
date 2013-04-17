from __future__ import unicode_literals

import ast
# import csv
# from multiprocessing import Process
# from threading import Thread
# import zipfile
# import zlib
# import tempfile

from dajax.core import Dajax
from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from dajaxice.utils import deserialize_form

# from django.contrib.auth.decorators import login_required
from django.forms.util import ErrorList
from django.core.context_processors import csrf
from django.template.loader import render_to_string
# from django.core.files import File

from settings import API_URL

# from apps.bioface.utils import ajax_login_required
from apps.bioface.forms import CreateOrganismForm, DownloadForm
from apps.bioface.utils import api_request
from apps.bioface.models import Download
from apps.bioface.tasks import loading_objects

@dajaxice_register
def download_objects(request, form, query_dict):
    dajax = Dajax()
    query_dict = ast.literal_eval(query_dict)
    form_data = deserialize_form(form)
    form = DownloadForm(data = form_data)
    if form.is_valid():
        del query_dict['params']['limit']
        del query_dict['params']['skip']
        # thread = Process(target = prepair_objects, kwargs = {'query_dict': query_dict})
        
        # thread = threading.Thread(target = daemon_test)
        # thread.daemon = True
        encoding = form.cleaned_data['encoding']
        object_download = Download.objects.create(
            encoding = encoding,
            user = request.user,
            description = form.cleaned_data['description'],
            status = 'expected')

        with_attributes = True if 'attributes' in form.cleaned_data['options'] else False
        with_sequences = True if 'sequences' in form.cleaned_data['options'] else False
        obj_id = object_download.id
        # loading_objects(
        #     query_dict = query_dict, 
        #     object_download_id = obj_id,
        #     with_attributes = with_attributes,
        #     with_sequences = with_sequences,
        #     encoding = encoding
        #     )
        download_task = loading_objects.delay(
            query_dict = query_dict, 
            object_download_id = obj_id,
            with_attributes = with_attributes,
            with_sequences = with_sequences,
            encoding = encoding
            )
        object_download.task_id = download_task.task_id
        object_download.save()

        
        # thread = Thread(target = prepair_objects, kwargs = {
        #     'query_dict': query_dict, 
        #     'object_download': obj_id,
        #     'with_attributes': with_attributes,
        #     'with_sequences': with_sequences,
        #     'encoding': encoding,
        # })
        # thread.start()
        msg = 'Ok'
        template_context = {'success_message': 'Downloading successfully begin. You can see the status or get file in "My downloads".'}
        dajax.script('success_adding_download();')
    else:
        msg = 'err'
        # template_context = {'success_message': 'Downloading successfully begin. You can see the status or get file in "My downloads".'}
    
    
    render = render_to_string('components/alert_messages.html', template_context)
    dajax.assign('.extra-message-block', 'innerHTML', render)
    
    # dajax.assign('#js_object_result_table', 'innerHTML', render)
    # dajax.script('stop_show_loading();')
    # dajax.alert(msg)
    return dajax.json()

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

# def prepair_objects(query_dict, object_download, with_attributes=False, with_sequences=False, encoding='utf-8'):
#     object_download = Download.objects.get(id = object_download)
#     content_dict = api_request(query_dict)
#     if content_dict.has_key('result'):
#         objects = content_dict['result']['objects']
#         print content_dict['result']
#         with tempfile.NamedTemporaryFile(delete=False) as obj_csvfile:
#             # spamwriter = csv.writer(obj_csvfile, delimiter=str(','), quotechar=str('|'), quoting=csv.QUOTE_MINIMAL)
#             spamwriter = UnicodeWriter(obj_csvfile, encoding=encoding)
#             col_list = []
#             attr_col_list = []
#             for key, val in objects[0].iteritems():
#                 if key == 'attributes':
#                     attr_col_list = [ attr['name'] for attr in val ]
#                 else:
#                     col_list.append(key)
#             col_list.extend(attr_col_list)

#             spamwriter.writerow(col_list)
#             for obj in objects:
#                 obj_vals = []
#                 obj_attrs_val = [ None for i in attr_col_list ]
#                 for key, val in obj.iteritems():
#                     if key == 'attributes':
#                         for attr in val:
#                             idx = attr_col_list.index(attr['name'])
#                             attr_value = attr['value']
#                             obj_attrs_val[idx] = attr_value
#                     else:
#                         obj_vals.append(val)

#                 obj_vals.extend(obj_attrs_val)
#                 print 22222, obj_vals
#                 # try:
#                 spamwriter.writerow(obj_vals)
#                 # except UnicodeEncodeError:
#                 #     print 666666, obj_vals

#         csv_files_list = [('objects.csv', obj_csvfile.name)]

#         if with_attributes:
#             # Get all attributes from select objects
#             if query_dict['params'].has_key('attributes_list'):
#                 del query_dict['params']['attributes_list']

#             content_dict = api_request(query_dict)
#             if content_dict.has_key('result'):
#                 objects = content_dict['result']['objects']

#                 with tempfile.NamedTemporaryFile(delete=False) as attr_csvfile:
#                     # spamwriter = csv.writer(attr_csvfile, delimiter=str(','), quotechar=str('|'), quoting=csv.QUOTE_MINIMAL)
#                     spamwriter = UnicodeWriter(attr_csvfile, encoding=encoding)
#                     attr_col_list = ['Objects']
#                     attr_col_list.extend([ attr['name'] for attr in objects[0]['attributes'] ])
#                     spamwriter.writerow(attr_col_list)
#                     for obj in objects:
#                         obj_attrs_val = [ None for i in attr_col_list ]
#                         for attr in obj['attributes']:
#                             idx = attr_col_list.index(attr['name'])
#                             obj_attrs_val[idx] = attr['value']
#                         obj_attrs_val[0] = obj['name']

#                         spamwriter.writerow(obj_attrs_val)

#                 csv_files_list.append(('attributes.csv', attr_csvfile.name))

#         if with_sequences:
#             # TODO
#             pass

#         zip_file_name = 'download_id_{}.zip'.format(object_download.id)
#         zip_file_path = DOWNLOADS_ROOT + zip_file_name
#         with zipfile.ZipFile(zip_file_path, 'w') as myzip:
            
#             compression = zipfile.ZIP_DEFLATED
#             for file_name, file_path in csv_files_list:
#                 myzip.write(file_path, arcname=file_name, compress_type=compression)

#         object_download.status = 'complete'
#         object_download.file_path = zip_file_name
#         object_download.save()

#     return True


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

# from apps.bioface.views import get_pagination_page
# @dajaxice_register
# # @ajax_login_required
# def pagination(request, page, method, query):
# 	query_dict = ast.literal_eval(query)
# 	print query_dict
# 	raise
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
