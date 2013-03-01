# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# from __future__ import print_function
from __future__ import absolute_import

import urllib
import httplib2 
import json

import ast

from django.conf import settings
from django import forms
from django.forms.formsets import formset_factory
from django.http import StreamingHttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from apps.bioface.utils import api_request, API_URL
from apps.bioface.forms import *

def create_sequence(request):
    template_name = 'create_sequence.html'
    if request.method == 'POST':
        form = CreateSequenceForm(request=request, data = request.POST)
        if form.is_valid():
            query_dict = {
            "method" : "add_sequence",
            "key": request.user.sessionkey,
            "params" : {
                "data" : {
                    # "name": "str",
                    # "ploid": int,
                    # "index": int, //номер последовательности в файле
                    # "is_ref": false, //является ли референсной
                    # "length": int, //длинна
                    # "comment": "str",
                    # "source": "str",
                    # "struct": "str",
                    # "regions": integer, //количество регионов
                    # "method": "str", //метод получения
                    # "seqf": "id", //id файла с последовательностями
                    # "tags": ["id", "id"],
                    # "accuracy" : float,
                    # "obj": "id", //id объекта к которому относится последовательность
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
                return redirect('update_object')
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


def get_pagination_page(page, query_dict):
    item_count = 5
    item_name = query_dict['method'].replace('get_', '')
    if not query_dict.has_key('params'):
        query_dict['params'] = {}

    # Monkey patch. Need for test exist next page, or not
    query_dict['params']['limit'] = item_count+1

    query_dict['params']['skip'] = item_count * (page-1)
    http_response, content_dict = api_request(query_dict)
    template_name, template_context = get_item_list_by_api(item_name, content_dict)
    items = template_context['items']
    if len(items) > item_count:
        next_page = True
        template_context['items'] = template_context['items'][:-1]
    else:
        next_page = False

    previous_page = True if page > 1 else False

    template_context.update({
        'has_next': next_page,
        'has_previous': previous_page,
        'next_page_number': page+1,
        'previous_page_number': page-1,
        'method': query_dict['method']
        # 'query': query_dict['params'],
    })

    return template_name, template_context

def test(request):
    return render_to_response('test.html', {}, context_instance=RequestContext(request))
