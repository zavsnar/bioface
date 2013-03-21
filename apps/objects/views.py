# -*- coding: utf-8 -*-
# from __future__ import unicode_literals
# from __future__ import print_function
from __future__ import absolute_import

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
from django.http import StreamingHttpResponse
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
from apps.objects.forms import CreateObjectForm, UpdateObjectForm, CreateOrganismForm, SelectObjects
from apps.objects.forms import OBJECT_FIELDS, OBJECT_FIELDS_CHOICES_WITH_TYPE

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


def update_object(request, object_id = 0):
    query_dict = {
        "method" : "get_object",
        "key": request.user.sessionkey,
        "params" : {
            "id" : int(object_id)
            # "attributes_list": ["attribute_id1", "attribute_id2",  ]
        }
    }
    content_dict = api_request(query_dict)
    if content_dict.has_key('result'):
        object_data = content_dict['result']['object']
        if object_data.has_key('attributes'):
            attr_dict = content_dict['result']['object'].pop('attributes')
        else:
            attr_dict = {}

        if request.method == 'POST':
            form = UpdateObjectForm(request=request, data = request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                query_dict = {
                    "method" : "update_object",
                    "key": request.user.sessionkey,
                    "params" : {
                        "id" : cd.pop('id'),
                        "version" : cd.pop('version'),
                        "attributes_autoexpand" : True,
                        "data" : {
                            "fields": {
                            #     "name" : name, //str
                            #     "lab_id":  Лабораторный идентификатор, //str
                            #     "organism": организм, //str
                            #     "source": источник, //str
                            #     "comment": comment, //str
                            #     "refs": ["id1", "id2"], //список id референсов
                            #     "tags": ["id", "id"], 
                            },
                            "attributes": [
                            #     ["attribute_id", "value1"],
                            #     etc...
                            ]
                        }
                    }
                }

                obj_fields = query_dict['params']['data']['fields']
                for key, value in form.cleaned_data.items():
                    print key, value
                    if value:
                        obj_fields[key] = value

                content_dict = api_request(query_dict)
                
                if content_dict.has_key('result'):
                # {u'error': {u'code': -32005,
                # u'data': u'(IntegrityError) duplicate key value violates unique constraint "objects_name_key"\nDETAIL:  Key (name)=(123) already exists.\n',
                # u'message': u'not unique'}}
                    messages.success(request, 'Object {0} with ID {1} and Version {2} successfully updated.'.format(
                        form.cleaned_data['name'], content_dict['result']['id'], content_dict['result']['version'])
                    )
                elif content_dict.has_key('error'):
                    messages.error(request, 'ERROR: {}'.format(content_dict['error']))

        else:
                # obj_fields = query_dict['params']['data']['fields']
                # for key, value in form.cleaned_data.items():
                #     obj_fields[key] = value

                # sequense_form = InlineSequenseForm(initial={})
                # formset = formset_factory(InlineSequenseForm, extra=2, can_delete=True)

                form = UpdateObjectForm(request = request, initial=object_data)

    elif content_dict.has_key('error'):
        form = UpdateObjectForm(request=request)
        messages.error(request, 'ERROR: {}'.format(content_dict['error']['data']))


    template_context = {
        'form': form,
        'attr_dict': attr_dict
        # 'formset': formset
    }

    return render_to_response('edit-object.html', template_context, context_instance=RequestContext(request))


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
            print attr_name_list
        else:
            attr_name_list = set([param_name for item in item_list for param_name in item.keys()])

        template_context = {'attr_name_list': attr_name_list, 'item_name': item_name, 'items': item_list}

    return template_name, template_context


def get_pagination_page(page, query_dict, paginate_by=5):
    item_name = query_dict['method'].replace('get_', '')
    if not query_dict.has_key('params'):
        query_dict['params'] = {}

    # Monkey patch. Need for test exist next page, or not
    query_dict['params']['limit'] = paginate_by+1

    query_dict['params']['skip'] = paginate_by * (page-1)
    print  777777, query_dict
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
    row_query_str=''
    fields = OBJECT_FIELDS
    saved_query_list = SavedQuery.objects.filter(user=request.user)

    if request.method == 'POST':
        form = SelectObjects(request=request, data = request.POST)
        
        query_history = ast.literal_eval(request.POST['query_history'])

        query_history_step = request.POST['query_history_step']
        # query_history_step = query_history_step.decode('utf8')
        if query_history_step:
            field_filters_dict_sort={}
            all_attr_type_dict = { key: atype for (key, item, atype) in form.fields['attributes_list'].choices }
            all_attr_type_dict.update(OBJECT_FIELDS_CHOICES_WITH_TYPE)
            if re.findall('\(.+\)', query_history_step):
                old_row_query_str, query_step_st = re.findall('(\(.+\)) AND (.+)', query_history_step)[0]
            else:
                old_row_query_str = ''
                query_step_st = query_history_step

            row_query_str = query_history_step

            if query_step_st:
                # query_step_st = query_step_st.decode('utf8')
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
                    print 888888888, attr_name
                    field_filters_dict_sort[i] = (attr_name, operation, attr_value.replace('"', ''), all_attr_type_dict[_attr_name])

        else:
            logic_operation = request.POST.get('select_operand')
            row_query_str = request.POST['row_query_str']
            old_row_query_re = re.findall('\(.+\)', row_query_str)
            old_row_query_str = old_row_query_re[0] if old_row_query_re else ''
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
            'row_query_str': row_query_str,
            'old_row_query_str': old_row_query_str,
            # 'attributes_from_organism': attributes_from_organism,
        })

        if form.is_valid():
            cd = form.cleaned_data
                # query_dict = ast.literal_eval(query_str)
            

            # query_dict['params'] = {}

            # if cd['organism']:
            row_query = 'organism = {}'.format(cd['organism'])

            if row_query_str:
                prep_row_query_str = row_query_str.replace(' AND ', ' & ').replace(' OR ', ' | ')
                row_query = row_query + ' & ' + prep_row_query_str
                print 9999, row_query

            attr_list=[]
            # if cd['attributes_list']:
            # query_dict['params']['attributes_list'] = cd['attributes_list']
            attr_list = cd['attributes_list']

            # query_dict['params']['query'] = row_query

            # if request.GET.has_key('order_by'):
            order_field = request.GET.get('order_by', 'name')
            # query_dict['params']['orderby'] = [[order_field, "acs"],]

            query_dict = {
                "method" : 'get_objects',
                "key": request.user.sessionkey,
                "params" : {
                    "count": 'true',
                    "query" : row_query,
                #     "limit" : int,
                #     "skip": int,
                    "orderby" : [(order_field, "acs"),],
                    "attributes_list": cd['attributes_list']
                }
            }

            try:
                content_dict = get_pagination_page(page=1, paginate_by=paginate_by, query_dict=query_dict)
                # print 77777, content_dict['result']['objects'][0]
                
            except socket.error:
                # TODO
                messages.error(request, 'Oops! Not connected to server.')
                return render_to_response("select_objects.html", template_context, context_instance=RequestContext(request))


            if content_dict.has_key('result'):
                if len(cd['display_fields']):
                    display_fields = cd['display_fields']
                else:
                    display_fields = fields
                print display_fields, ['name'].extend(cd['display_fields']), fields

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

                # Monkey patch. If list of objects longer items per page, that show next button
                if len(object_list) > paginate_by:
                    next_page = True
                    object_list = object_list[:-1]
                else:
                    next_page = False

                previous_page = False

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
                    'next_page_number': 2,
                    # 'previous_page_number': 1,
                    'paginate_by': paginate_by,
                    'objects_count': objects_count,  
                })

            else:   
                msg = content_dict['error']['message']
                messages.error(request, 'API ERROR: {}. {}'.format(msg, content_dict['error']['data']))

            query_dict_str = mark_safe(json.dumps(query_dict))
            template_context.update({
                # 'query_str': row_query,
                'query_dict_str': query_dict_str
                })
        else:
            print 55555

    # For saved query
    elif request.method == 'GET' and request.GET.get('saved_query', None):
        query_name = request.GET['saved_query']
        saved_query = SavedQuery.objects.get(name=query_name)
        form_data = {'organism': saved_query.organism_id, 'display_fields': saved_query.display_fields, 'attributes_list': saved_query.attributes_list}
        print 888, form_data
        form = SelectObjects(request=request, data=form_data)
        # field_filters_dict_sort = saved_query.filter_fields
        if saved_query.filter_fields.items():
            field_filters_dict_sort = {}
            for key, q in saved_query.filter_fields.items():
                if key:
                    q[1] = mark_safe(q[1])
                    field_filters_dict_sort[int(key)] = q

        # if field_filters_dict:
        #     field_filters_dict_sort={}
        #     for key, q in field_filters_dict.items():
        #         if key:
        #             q[1] = mark_safe(q[1])
        #             field_filters_dict_sort[int(key)] = q
        #     print 44444, field_filters_dict_sort
        # attributes_from_organism = [ value[1] for value in form.fields['attributes_list'].choices ]
        row_query_str = saved_query.query_str
        old_row_query_re = re.findall('\(.+\)', row_query_str)
        old_row_query_str = old_row_query_re[0] if old_row_query_re else ''


        template_context.update({
            # 'logic_operation': saved_query.logic_operation,
            'logic_operation': "ALL",
            'row_query_str': row_query_str,
            'old_row_query_str': old_row_query_str,
            # 'row_query_str': '',
            # 'attributes_from_organism': attributes_from_organism,
        })
    else:
        form = SelectObjects(request=request)

    query_history = []

    if row_query_str:
        step = True
        while step:
            _query_re = re.findall('\((.+)\)', row_query_str)
            step = _query_re[0] if _query_re else None
            if step:
                query_history.append(step)
                row_query_str = step
        query_history.reverse()

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
