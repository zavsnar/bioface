# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# from __future__ import print_function
from __future__ import absolute_import, division

import math
import re
import urllib
import httplib2 
import socket
import json
from dateutil.parser import parse as datetime_parse

import ast

from itertools import repeat

from django.conf import settings
from django import forms
from django.forms.formsets import formset_factory
from django.http import StreamingHttpResponse, Http404
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.safestring import mark_safe
from django.utils.encoding import smart_text, force_text, smart_unicode


from apps.bioface.utils import api_request
from apps.bioface.models import SavedQuery
from apps.bioface.forms import DownloadForm
from apps.objects.forms import CreateObjectForm, UpdateObjectForm, \
    CreateOrganismForm, SelectObjects
from apps.objects.forms import OBJECT_FIELDS, OBJECT_FIELDS_CHOICES_WITH_TYPE

@login_required
def create_object(request):
    template_name = 'create_object.html'
    if request.method == 'POST':
        form = CreateObjectForm(request=request, data = request.POST)
        if form.is_valid():
            query_dict = {
                "method" : "add_object",
                "key": request.user.sessionkey,
                "params" : {
                    # "attributes_autoexpand" : true,
                    "data" : {
                        "fields": {
                        #     "name" : name, //str
                        #     "lab_id":  Лабораторный идентификатор, //str
                        #     "organism": организм, //str
                        #     "source": источник, //str
                        #     "comment": comment, //str
                        #     "refs": ["id1", "id2"], //список id референсов
                        #     "tags": ["id", "id"], //список id тегов
                             },
                        # "attributes": [["attribute_id", "value1"],
                        #     etc...
                        # ]
                        }
                    }
                }

            obj_fields = query_dict['params']['data']['fields']
            for key, value in form.cleaned_data.items():
                if key == 'organism':
                    value = int(value)
                obj_fields[key] = value

            content_dict = api_request(query_dict)
            
            if content_dict.has_key('result'):
            # {u'error': {u'code': -32005,
            # u'data': u'(IntegrityError) duplicate key value violates unique constraint "objects_name_key"\nDETAIL:  Key (name)=(123) already exists.\n',
            # u'message': u'not unique'}}
                messages.success(request, 'Object {0} with ID {1} and Version {2} successfully created.'.format(
                    form.cleaned_data['name'], content_dict['result']['id'], content_dict['result']['version'])
                )
                return redirect('update_object', object_id=content_dict['result']['id'])
            elif content_dict.has_key('error'):
                messages.error(request, 'ERROR: {}'.format(content_dict['error']['data']))

    else:
        form = CreateObjectForm(request=request)

    add_organism_form = CreateOrganismForm()

    template_context = {
        'form': form,
        'additional_form': add_organism_form
    }
    return render_to_response(template_name, template_context, context_instance=RequestContext(request))

@login_required
def update_object(request, object_id = 0):
    try:
        object_id = int(object_id)
    except ValueError:
        raise Http404

    if request.method == 'POST':
        form = UpdateObjectForm(request=request, data = request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            query_dict = {
                "method" : "update_object",
                "key": request.user.sessionkey,
                "params" : {
                    "id" : cd.get('id'),
                    "version" : cd.get('version'),
                    "attributes_autoexpand" : False,
                    "data" : {
                        "fields": {
                            "name" : cd.get('name'),
                            "lab_id": cd.get('lab_id'),
                            "organism": cd.get('organism'),
                            "source": cd.get('source'),
                            "comment": cd.get('comment'),
                        #     "refs": ["id1", "id2"], //список id референсов
                            # "tags": cd.get('tags'),
                            # "files": cd.get('files_id').split(',')
                        },
                        # "attributes": [
                        #     ["attribute_id", "value1"],
                        #     etc...
                        # ]
                    }
                }
            }

            if cd.get('tags', ''):
                query_dict['params']['data']['fields']['tags'] = form.tags_id_list

            if request.POST.get('files_dict', ''):
                files_dict = ast.literal_eval(request.POST['files_dict'])
                query_dict['params']['data']['fields']['files'] = files_dict.keys()

            if request.POST.get('updated_attributes', ''):
                attribute_dict = ast.literal_eval(request.POST['updated_attributes'])
                if attribute_dict:
                    query_dict['params']['data']['attributes'] = attribute_dict.items()
                    query_dict['params']['attributes_autoexpand'] = True

            content_dict = api_request(query_dict)
            # form._changed_data = {'source': '123'}
            if content_dict.has_key('result'):
            # {u'error': {u'code': -32005,
            # u'data': u'(IntegrityError) duplicate key value violates unique constraint "objects_name_key"\nDETAIL:  Key (name)=(123) already exists.\n',
            # u'message': u'not unique'}}
                messages.success(request, 'Object "{}" successfully updated.'.format(cd.get('name')))

                form.object_version = content_dict['result']['version']
                # files_id = cd.get('files_id')

            elif content_dict.has_key('error'):
                messages.error(request, 'ERROR: {}'.format(content_dict['error']))

    query_dict = {
        "method" : "get_object",
        "key": request.user.sessionkey,
        "params" : {
            "id" : object_id,
            "nulls_filler": "",
            # "attributes_list": ["attribute_id1", "attribute_id2",  ]
        }
    }
    content_dict = api_request(query_dict)
    if content_dict.has_key('result'):
        object_data = content_dict['result']['object']
        if object_data.has_key('attributes'):
            attr_query_dict = {
                "method" : "get_attributes",
                "key": request.user.sessionkey,
                "params" : {
                    "query" : "organism = {}".format(object_data['organism']),
                    "orderby" : [["name", "asc"]]
                }
            }
            attr_content_dict = api_request(attr_query_dict)
            if attr_content_dict.has_key('result'):
                attr_content_list = { attr['name']: attr['description'] for attr in attr_content_dict['result']['attributes'] if attr['atype'] in ('nominal', 'scale') }
            attr_list = content_dict['result']['object'].pop('attributes')
            for attr in attr_list:
                if attr['type'] == 'nominal':
                    attr['options'] = attr_content_list[attr["name"]]['items']
                elif attr['type'] == 'scale':
                    opts = attr_content_list[attr["name"]]['scale']
                    attr['options'] = map(lambda d: d['name'], sorted(opts, key=lambda opt: opt['weight']))
        else:
            attr_list = {}

        files_dict = { f['id']: f['name'] for f in object_data['files'] }

        if request.method == 'GET':
            form = UpdateObjectForm(request = request, initial=object_data)

        template_context = {
            'form': form,
            'attr_list': attr_list,
            'attr_content_list': attr_content_list,
            'object_data': object_data,
            'files_dict': files_dict
            # 'formset': formset
        }

    elif content_dict.has_key('error'):
        form = UpdateObjectForm(request=request)
        messages.error(request, 'ERROR: {}'.format(content_dict['error']['data']))

        template_context = {}

    return render_to_response('edit-object.html', template_context, context_instance=RequestContext(request))

@login_required
def create_organism(request):
    if request.method == 'POST':
        form = CreateOrganismForm(data = request.POST)
        if form.is_valid():
            query_dict = {
                "method" : "create_object",
                "key": request.user.sessionkey,
                "params" : {
                    # "attributes_autoexpand" : true,
                    "data" : {
                        "fields": {
                        #     "name" : name, //str
                        #     "lab_id":  Лабораторный идентификатор, //str
                        #     "organism": организм, //str
                        #     "source": источник, //str
                        #     "comment": comment, //str
                        #     "refs": ["id1", "id2"], //список id референсов
                        #     "tags": ["id", "id"], //список id тегов
                             },
                        # "attributes": [["attribute_id", "value1"],
                        #     etc...
                        # ]
                        }
                    }
                }

            obj_fields = query_dict['params']['data']['fields']
            for key, value in form.cleaned_data.items():
                obj_fields[key] = value

            content_dict = api_request(query_dict)
            
            if content_dict.has_key('result'):
            # {u'error': {u'code': -32005,
            # u'data': u'(IntegrityError) duplicate key value violates unique constraint "objects_name_key"\nDETAIL:  Key (name)=(123) already exists.\n',
            # u'message': u'not unique'}}
                messages.success(request, 'Object {0} with ID {1} and Version {2} successfully created.'.format(
                    form.cleaned_data['name'], content_dict['result']['id'], content_dict['result']['version'])
                )
            elif content_dict.has_key('error'):
                messages.error(request, 'ERROR: {}'.format(content_dict['error']['data']))

    else:
        form = CreateOrganismForm()

    template_context = {
        'form': form,
    }
    return render_to_response('create_object.html', template_context, context_instance=RequestContext(request))


def get_item_list_by_api(item_name, content_dict):
    template_name = 'item_list.html'
    template_context = {'items': []}
    item_list = content_dict['result'].get(item_name, [])
    if item_list:
        if item_name == "objects":
            attr_name_list = [ attr['name'] for attr in content_dict['result']['attributes'] ]
        else:
            attr_name_list = set([param_name for item in item_list for param_name in item.keys()])

        template_context = {
            'attr_name_list': attr_name_list, 
            'item_name': item_name, 
            'items': item_list
            }

    return template_name, template_context


def get_pagination_page(page, query_dict, paginate_by=5):
    item_name = query_dict['method'].replace('get_', '')
    if not query_dict.has_key('params'):
        query_dict['params'] = {}

    query_dict['params']['limit'] = paginate_by

    query_dict['params']['skip'] = paginate_by * (page-1)
    content_dict = api_request(query_dict)

    return content_dict
    
    # template_name, template_context = get_item_list_by_api(item_name, content_dict)
    # items = template_context['items']
    # if len(items) > paginate_by:
    #     next_page = True
    #     template_context['items'] = template_context['items'][:-1]
    # else:
    #     next_page = False

    # previous_page = True if page > 1 else False

    # template_context.update({
    #     'has_next': next_page,
    #     'has_previous': previous_page,
    #     'next_page_number': page+1,
    #     'previous_page_number': page-1,
    #     'method': query_dict['method']
    #     # 'query': query_dict['params'],
    # })

    # return template_name, template_context

def test(request):
    return render_to_response('test.html', {}, context_instance=RequestContext(request))

from ajaxuploader.views import AjaxFileUploader
import_uploader = AjaxFileUploader()

@login_required
def get_objects(request):
    paginate_by = 10
    template_context = {}
    field_filters_dict_sort = {'': []}
    raw_query_str=''
    fields = OBJECT_FIELDS
    saved_query_list = SavedQuery.objects.filter(user=request.user)
    query_history = []

    if request.method == 'POST':
        form = SelectObjects(request=request, data = request.POST)
        query_history = ast.literal_eval(request.POST['query_history'])

        # query_history_step = query_history_step.decode('utf8')

        # Load from history
        query_history_step = request.POST['query_history_step']
        if query_history_step:
            where_search = ''
            field_filters_dict_sort={}
            all_attr_type_dict = { key: atype for (key, item, atype) in form.fields['attributes_list'].choices }
            all_attr_type_dict.update(OBJECT_FIELDS_CHOICES_WITH_TYPE)
            if re.findall('\(.+\)', query_history_step):
                old_raw_query_str, query_step_st = re.findall('(\(.+\)) AND (.+)', query_history_step)[0]
            else:
                old_raw_query_str = ''
                query_step_st = query_history_step

            raw_query_str = query_history_step

            if query_step_st:
                if ' AND ' in query_step_st:
                    logic_rel = ' AND '
                    logic_operation = 'ALL'
                else:
                    logic_rel = ' OR '
                    logic_operation = 'ANY'

                for i, attr in enumerate(query_step_st.split(logic_rel)):
                    if attr.find('"') != -1:
                        attr_name, operation, attr_value = re.findall('(.+) (.+) (".+")', attr)[0]
                    else:
                        attr_name, operation, attr_value = attr.split()
                    # print attr_name.encode('utf8')
                    _attr_name = attr_name.replace('attr.', '') if attr_name.startswith('attr.') else attr_name
                    # print attr_name.decode('utf8')
                    field_filters_dict_sort[i] = (attr_name, operation, attr_value.replace('"', ''), all_attr_type_dict[_attr_name])

        else:
            where_search = request.POST.get('where_search')
            logic_operation = request.POST.get('select_operand_in') if where_search == 'search_in_results' else request.POST.get('select_operand')
            raw_query_str = request.POST['raw_query_str']
            old_raw_query_re = re.findall('\(.+\)', raw_query_str)
            old_raw_query_str = old_raw_query_re[0] if old_raw_query_re else ''
            field_filters_dict = ast.literal_eval(request.POST['field_filters_dict'])
            if field_filters_dict:
                field_filters_dict_sort={}
                for key, q in field_filters_dict.items():
                    if key:
                        q[1] = mark_safe(q[1])
                        field_filters_dict_sort[int(key)] = [ s.decode('utf8') for s in q ]
        # attributes_from_organism = [ value[1] for value in form.fields['attributes_list'].choices ]

        # attributes_from_organism = form.fields['attributes_list'].choices
        # print 77777, attributes_from_organism
        # raise
        template_context.update({
            'logic_operation': logic_operation,
            'raw_query_str': raw_query_str,
            'old_raw_query_str': old_raw_query_str,
            'query_history_step': query_history_step
            # 'attributes_from_organism': attributes_from_organism,
        })

        if form.is_valid():
            cd = form.cleaned_data
            paginate_by = int(cd['paginate_by'])
            raw_query = 'organism = {}'.format(cd['organism'])

            if raw_query_str:
                prep_raw_query_str = raw_query_str.replace(' AND ', ' & ').replace(' OR ', ' | ')
                raw_query = raw_query + ' & (' + prep_raw_query_str + ')'

            attr_list=[]
            attr_list = cd['attributes_list']

            # if request.GET.has_key('order_by'):
            order_field = request.GET.get('order_by', 'name')
            order_field = cd['sort_by'] if cd['sort_by'] in OBJECT_FIELDS else 'attr.' + cd['sort_by']

            query_dict = {
                "method" : 'get_objects',
                "key": request.user.sessionkey,
                "params" : {
                    "count": 'true',
                    "query" : raw_query,
                    "nulls_filler": "n/a",
                #     "limit" : int,
                #     "skip": int,
                    "orderby" : [(order_field, "asc"),],
                    "attributes_list": cd['attributes_list']
                }
            }

            try:
                content_dict = get_pagination_page(page=1, paginate_by=paginate_by, query_dict=query_dict)
            except socket.error:
                # TODO
                messages.error(request, 'Oops! Not connected to server.')
                return render_to_response("select_objects.html", template_context, context_instance=RequestContext(request))


            if content_dict.has_key('result'):
                if len(cd['display_fields']):
                    display_fields = cd['display_fields']
                else:
                    display_fields = fields

                objects_count = content_dict['result']['total_count']

                object_list = []
                for obj in content_dict['result']['objects']:
                    object_fields=[]
                    for field in display_fields:
                        if field in ('created', 'modified'):
                            time_value = datetime_parse(obj[field])
                            field_value = time_value.strftime("%Y-%m-%d %H:%M:%S")
                            object_fields.append( (field, field_value) )
                        else:
                            object_fields.append( (field, obj[field]) )
                    
                    if obj.has_key('attributes'):
                        object_attrs = [ None for i in attr_list ]
                        for obj_attr in obj['attributes']:
                            attr_index = attr_list.index(obj_attr['name'])
                            object_attrs[attr_index] = obj_attr
                    else:
                        object_attrs = []

                    object_list.append(
                        {'object_name': obj['name'],
                        'url': reverse('update_object', kwargs={'object_id': obj['id']}),
                        'fields' :object_fields,
                        # 'attrs': [ d for attr in attr_list for d in obj['attributes'] if d['name'] == attr ]
                        'attrs': object_attrs,
                    })

                previous_page = False
                next_page = True if int(objects_count) > paginate_by else False

                pages_count = int(math.ceil(objects_count/paginate_by))
                if pages_count < 12:
                    pages = range(1, pages_count+1)
                else:
                    pages = range(1, 4)
                    pages.append('...')
                    pages.extend(range(pages_count-2, pages_count+1))

                    # object_list = object_list[:-1]
                # else:
                #     next_page = False

                if query_history:
                    # if query_history[-1]['query'] == raw_query_str.encode('utf8'):
                    #     query_history[-1]['count'] = objects_count
                    if query_history_step:
                        # Loading from history
                        for step in query_history:
                            if step['query'] == query_history_step.encode('utf8'):
                                step['count'] = objects_count
                                idx = query_history.index(step)
                                query_history = query_history[:idx+1]
                                break
                    elif where_search == 'search_in_results' and query_history[-1]['query'] != raw_query_str.encode('utf8'):
                    # elif len(query_history) > 1 and query_history[-2]['query'] == old_raw_query_str[1:-1].encode('utf8'):
                        # Search in result
                        query_history.append({'query': raw_query_str, 'count': objects_count})
                    else:
                        # Change current query or new query
                        query_history[-1] = {'query': raw_query_str, 'count': objects_count}
                else:
                    query_history.append({'query': raw_query_str, 'count': objects_count})
                # print 99999, query_history

                display_fields_str = mark_safe(json.dumps(display_fields))
                template_context.update({
                    # 'fields': fields,
                    'display_fields': display_fields,
                    'display_fields_str': display_fields_str,
                    'attributes': attr_list,
                    'object_list': object_list,
                    'object_download_form': DownloadForm(),

                    'has_next': next_page,
                    'has_previous': previous_page,
                    'pages': pages,
                    'this_page': 1,
                    'next_page_number': 2,
                    # 'previous_page_number': 1,
                    'paginate_by': paginate_by,
                    'items_count': objects_count,  
                })
            else:   
                msg = content_dict['error']['message']
                messages.error(request, 
                    'API ERROR: {}. {}'.format(msg, content_dict['error']['data']))

            query_dict_str = mark_safe(json.dumps(query_dict))
            template_context.update({
                # 'query_str': raw_query,
                'query_dict_str': query_dict_str
                })
        else:
            print 55555

    # For saved query
    elif request.method == 'GET' and request.GET.get('saved_query', None):
        query_name = request.GET['saved_query']
        saved_query = SavedQuery.objects.get(name=query_name)
        form_data = {
            'organism': saved_query.organism_id, 
            'display_fields': saved_query.display_fields, 
            'attributes_list': saved_query.attributes_list,
            'paginate_by': saved_query.paginate_by, 
            'sort_by': saved_query.sort_by
            }
        form = SelectObjects(request=request, data=form_data)
        # field_filters_dict_sort = saved_query.filter_fields
        if saved_query.filter_fields.items():
            field_filters_dict_sort = {}
            for key, q in saved_query.filter_fields.items():
                if key:
                    q[1] = mark_safe(q[1])
                    field_filters_dict_sort[int(key)] = q

        raw_query_str = saved_query.query_str
        old_raw_query_re = re.findall('\(.+\)', raw_query_str)
        old_raw_query_str = old_raw_query_re[0] if old_raw_query_re else ''


        if raw_query_str:
            step = True
            raw_query_str_iter = raw_query_str
            query_history.append({'query': raw_query_str, 'count': ''})
            while step:
                _query_re = re.findall('\((.+)\)', raw_query_str_iter)
                step = _query_re[0] if _query_re else None
                if step:
                    query_history.append({'query': step, 'count': ''})
                    raw_query_str_iter = step

            
            query_history.reverse()

        template_context.update({
            # 'logic_operation': saved_query.logic_operation,
            'logic_operation': "ALL",
            'raw_query_str': raw_query_str,
            'old_raw_query_str': old_raw_query_str,
            # 'raw_query_str': '',
            # 'attributes_from_organism': attributes_from_organism,
        })
    else:
        form = SelectObjects(request=request)

    attributes_from_organism = form.fields['attributes_list'].choices

    template_context.update({
        'form': form, 
        'method': 'get_objects',
        'saved_query_list': saved_query_list,
        'fields': fields,
        'fields_with_type': OBJECT_FIELDS_CHOICES_WITH_TYPE,
        'field_filters_dict': field_filters_dict_sort,
        'attributes_from_organism': attributes_from_organism,
        'query_history': query_history
        })

    return render_to_response("select_objects.html", template_context, context_instance=RequestContext(request))
