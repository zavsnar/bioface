# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# from __future__ import print_function
from __future__ import absolute_import

import urllib
import httplib2 
import socket
import json

import ast

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

from apps.bioface.utils import api_request
from apps.objects.forms import *

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

            http_response, content_dict = api_request(query_dict)
            
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
    http_response, content_dict = api_request(query_dict)
    if content_dict.has_key('result'):
        object_data = content_dict['result']['object']
        print 7777, object_data
        if object_data.has_key('attributes'):
            attr_dict = content_dict['result']['object'].pop('attributes')
        else:
            attr_dict = {}

        if request.method == 'POST':
            form = UpdateObjectForm(request=request, data = request.POST)
            print 3333, request.POST
            if form.is_valid():
                cd = form.cleaned_data
                print 77777, cd
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

                print 1111, query_dict
                http_response, content_dict = api_request(query_dict)
                print 2222, content_dict
                
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

            http_response, content_dict = api_request(query_dict)
            
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
    http_response, content_dict = api_request(query_dict)

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
    response_api_query_dict = {'': []}
    fields = OBJECT_FIELDS
    template_name = "select_objects.html"
    if request.method == 'POST':
        form = SelectObjects(request=request, data = request.POST)
        
        api_query_dict = ast.literal_eval(request.POST['row_query_dict'])
        row_query_str = request.POST['row_query_str']
        logic_operation = request.POST.get('select_operand')
        
        if api_query_dict:
            response_api_query_dict={}
            for key, q in api_query_dict.items():
                if key:
                    q[1] = mark_safe(q[1])
                    response_api_query_dict[int(key)] = q
            print 44444, response_api_query_dict
        attributes_from_organism = [ value[1] for value in form.fields['attributes_list'].choices ]

        template_context.update({
            'logic_operation': logic_operation,
            'row_query_str': row_query_str,
            'attributes_from_organism': attributes_from_organism,
        })
        if form.is_valid():
            cd = form.cleaned_data
                # query_dict = ast.literal_eval(query_str)
            query_dict = {
                "method" : 'get_objects',
                "key": request.user.sessionkey,
                # "params" : {
                #     "query" : "field > 12 and (field2 = green and field64 > big)",
                #     "limit" : int,
                #     "skip": int,
                #     "orderby" : [["field_name", "asc"], ["field_name2", "desc"]]
                #     "attributes_list": ["attribute_name1", "attribute_name2",  ]
                # }
            }

            query_dict['params'] = {}

            # if cd['organism']:
            row_query = 'organism = {}'.format(cd['organism'])

            if row_query_str:
                prep_row_query_str = row_query_str.replace(' AND ', ' & ').replace(' OR ', ' | ')
                row_query = row_query + ' & ' + prep_row_query_str
                print 9999, row_query

            attr_list=[]
            if cd['attributes_list']:
                query_dict['params']['attributes_list'] = cd['attributes_list']
                attr_list = cd['attributes_list']

            query_dict['params']['query'] = row_query

            if request.GET.has_key('order_by'):
                order_field = request.GET['order_by']
                query_dict['params']['orderby'] = [[order_field, "acs"],]

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
                print display_fields, ['name'].extend(cd['display_fields']), fields

                object_list = []
                for obj in content_dict['result']['objects']:
                    object_list.append(
                        {'object_name': obj['name'],
                        'url': reverse('update_object', kwargs={'object_id': obj['id']}),
                        'fields' :[ obj[field] for field in display_fields ],
                        'attrs': [ obj['attributes'][attr] for attr in attr_list ]})

                # Monkey patch. If list of objects longer items per page, that show next button
                if len(object_list) > paginate_by:
                    next_page = True
                    object_list = object_list[:-1]
                else:
                    next_page = False

                previous_page = False

                display_fields_str = mark_safe(json.dumps(display_fields))
                template_context.update({
                    'fields': fields,
                    'display_fields': display_fields,
                    'display_fields_str': display_fields_str,
                    'attributes': attr_list,
                    'object_list': object_list,

                    'has_next': next_page,
                    'has_previous': previous_page,
                    'next_page_number': 2,
                    # 'previous_page_number': 1,
                    'paginate_by': paginate_by,    
                })

            else:   
                msg = content_dict['error']['message']
                messages.error(request, 'API ERROR: {}. {}'.format(msg, content_dict['error']['data']))

            query_dict_str = mark_safe(json.dumps(query_dict))
            template_context.update({
                'query_str': row_query,
                'query_dict_str': query_dict_str
                })
        else:
            print 55555
    else:
        form = SelectObjects(request=request)

    template_context.update({
        'form': form, 
        'method': 'get_objects',
        'fields': fields,
        'api_query_dict': response_api_query_dict,
        })

    return render_to_response("select_objects.html", template_context, context_instance=RequestContext(request))
