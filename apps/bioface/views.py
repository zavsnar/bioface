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
from apps.bioface.models import Download

def index(request):
    return redirect('select_objects')

def alter_index(request):
    template_name = "test_index.html"
    template_name = "alter_index.html"
    return render_to_response( template_name, {},
        context_instance=RequestContext(request))

def signin(request):
    # https://10.0.1.204:5000
    # a@a.ru 123

    if request.method == 'POST':
        form = AuthenticationForm(data = request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:

                    # http = httplib2.Http(disable_ssl_certificate_validation=True)
               
                    query = {
                        "method" : "login",
                        "params" : {
                            "email": username,
                            "password": password
                            }
                        }

                    # response, content = http.request(API_URL, 'POST', body = json.dumps(query), headers = headers)

                    # response = json.loads(content)

                    # Login in service by API
                    content_dict = api_request(query)

                    if not content_dict.has_key('error'):
                        sessionkey = content_dict['result']['key']

                        # Django login
                        login(request, user)
                        user.sessionkey = sessionkey
                        user.save()
                        messages.success(request, "You successfully logged.")
                        redirect_url = request.GET.get('next') if request.GET.get('next', None) else '/'
                        print request.GET.get('next', None)
                        return redirect(redirect_url)
                    else:
                        msg = content_dict['error']['message']
                        messages.error(request, msg)
                        # print 1111, form._errors
                        # form._errors[forms.NON_FIELD_ERRORS] = form.error_class( (msg,))
                        
    else:
        form = AuthenticationForm()

    return render_to_response("login.html", {'form': form},
        context_instance=RequestContext(request))


def logout(request):
    user = getattr(request, 'user', None)
    redirect_url = request.GET.get('next') if request.GET.get('next', None) else '/'
    if hasattr(user, 'is_authenticated') and user.is_authenticated():
        headers = {'Content-type': 'application/json'}
        http = httplib2.Http(disable_ssl_certificate_validation=True)
                   
        query = {
            "method" : "logout",
            "params": {
                "key": request.user.sessionkey
                }
        }
        response, content = http.request(API_URL, 'POST', body = json.dumps(query), headers = headers)
        response = json.loads(content)

        if response['result'] == "bye":
            auth_logout(request)
        else:
            messages.error(request, response)

    return redirect(redirect_url)

def registration(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            # logout( request )
            new_user = authenticate(username=request.POST['username'],
                                    password=request.POST['password1'])
            auth_login(request, new_user)
            return redirect("/")
    else:
        form = RegistrationForm()

        
    return render_to_response("registration.html", {'form': form},
        context_instance=RequestContext(request))

@login_required
def downloads_list(request):
    from celery.result import BaseAsyncResult
    expected_downloads = Download.objects.filter(user=request.user, status="expected")
    for d in expected_downloads:
        task = BaseAsyncResult(d.task_id)
        if task.ready():
            if task.successful():
                d.file_path = task.result
                d.status = 'complite'
            else:
                # TODO
                status = task.status
                pass
            d.save()

    downloads = Download.objects.filter(user=request.user).order_by('-created')

    return render_to_response("download_list.html", {'downloads': downloads},
        context_instance=RequestContext(request))

def create_attribute(request):
    description_errors=[]
    if request.method == 'POST':
        form = CreateAttributeForm(request = request, data = request.POST)
        print request.POST
        # print 2222, request.POST['descr-nominal']
        rp = request.POST
        
        if form.is_valid():
            atype = rp.get('atype')
            cd = form.cleaned_data
            default_name = 'descr_{}_default'.format(atype)
            default_value = cd.get(default_name, rp.get(default_name))
            primary = bool(rp.get('primary'))

            if atype == 'integer':
                description_dict = {'default': int(default_value)}
            elif atype == 'string':
                description_dict = {'default': default_value}
            elif atype == 'float':
                description_dict = {'default': float(default_value)}
            elif atype == 'nominal':
                # default_value = rp.get('descr-nominal-default')
                nominal_list = cd.get('descr_nominal')
                description_dict = {"default": default_value, "items": nominal_list}
            elif atype == 'scale':
                # default_value = rp.get('descr-{}-default'.format(atype))
                
                # {"default": str, "scale": [{name: str, weight: int},...]}
                scale_list=[]
                for i, scale in enumerate(cd.get('descr_scale')):
                    scale_list.append({'name': scale, 'weight': i})
                
                # for _l in cd.get('descr_{}'.format(atype)).split('; '):
                #     name, weight = _l.split(', ')
                #     scale_list.append({'name': name, 'weight': int(weight)})

                description_dict = {"default": default_value, "scale": scale_list}
                # scale_dict = map(lambda x: x.split(', '), rp.get('descr-nominal').split('; '))
            elif atype == 'range':
                description_dict = {
                    "default": default_value, 
                    "upper": cd.get('descr_range_from'), 
                    "lower": cd.get('descr_range_to')
                    }

            query_dict = {
                "method" : "new_attribute",
                "key": request.user.sessionkey,
                "params" : {
                    "data" : {
                        "name": form.cleaned_data['name'],
                        "organism": int(form.cleaned_data['organism']),
                        "atype": form.cleaned_data['atype'],
                        "descr": description_dict,
                        "primary": primary
                    }
                }
            }
            print 333, query_dict

            content_dict = api_request(query_dict)
            
            print 5555, content_dict

            if content_dict.has_key('result'):
            # {u'error': {u'code': -32005,
            # u'data': u'(IntegrityError) duplicate key value violates unique constraint "objects_name_key"\nDETAIL:  Key (name)=(123) already exists.\n',
            # u'message': u'not unique'}}
                messages.success(request, 'Attribute {0} with ID {1} and Version {2} successfully created.'.format(
                    form.cleaned_data['name'], content_dict['result']['id'], content_dict['result']['version'])
                )
            elif content_dict.has_key('error'):
                if 'Key ({0})=({1}) already exists.'.format('name', cd['name']) in content_dict['error']['data']:
                    form.errors['name'] = form.error_class([content_dict['error']['message']])
                else:
                    messages.error(request, 'ERROR: {}'.format(content_dict['error']['data']))
                # '(IntegrityError) duplicate key value violates unique constraint "attrdescrs_name_key" DETAIL: Key (name)=(test_attr2) already exists.'
        else:
            form.fields['descr_nominal'].value = rp.getlist('descr_nominal')
            form.fields['descr_scale'].value = rp.getlist('descr_scale')

    else:
        form = CreateAttributeForm(request = request)


    template_context = {
        'form': form,
        'description_errors': description_errors,
    }
    return render_to_response('create_attribute.html', template_context, context_instance=RequestContext(request))


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

@login_required
def create_update_item(request):
    template_context = {}
    if request.method == 'POST':
        prepare_form = QueryMethodForm(data = request.POST)
        form = add_update_segment_form(request=request, data = request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            # Prepare query
            query_str = cd['request'].replace('"', "'").replace('\n', '')
            # Convert str to dict
            # query_dict = ast.literal_eval(query_str)
            query_dict = {
                "method" : cd['method'],
                "key": request.user.sessionkey,
                # "params" : {
                #     # "query" : "reference_id = id",
                #     "limit" : cd['limit'],
                #     "skip" : cd['skip'],
                #     # "orderby" : [["field_name", "acs"], ["field_name2", "desc"]]
                # }
            }
            template_name, template_context = get_pagination_page(page, query_dict)

            template_context.update({
                'query_dict': query_dict,
                })
    else:
        prepare_form = QueryMethodForm()
        # form = add_update_segment_form(request=request)

    template_context.update({
        # 'form': form, 
        'prepare_form': prepare_form
        })

    return render_to_response('create_update_item.html', template_context, context_instance=RequestContext(request))
    # return render_to_response('test.html', template_context, context_instance=RequestContext(request))


def get_item_by_api():
    template_name = 'item_detail.html'


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
    content_dict = api_request(query_dict)
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

@login_required
def request_api_page(request, method=None):
    response=''
    template_context={}
    template_name = "request_page.html"
    if request.method == 'POST':
        form = GetRequestAPIForm(data = request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            if cd.has_key('request'):
                # Prepare query
                query_str = cd['request'].replace('"', "'").replace('\n', '')
                # Convert str to dict
                # query_dict = ast.literal_eval(query_str)
            query_dict = {
                "method" : cd['method'],
                "key": request.user.sessionkey,
                # "params" : {
                #     # "query" : "reference_id = id",
                #     "limit" : cd['limit'],
                #     "skip" : cd['skip'],
                #     # "orderby" : [["field_name", "acs"], ["field_name2", "desc"]]
                # }
            }
            if cd.has_key('row_query'):
                query_dict['params'] = {}
                query_dict['params']['query'] = cd['row_query']

            page = request.GET.get('page', 1)
            template_name, template_context = get_pagination_page(page, query_dict)


            template_context.update({
                'query_dict': query_dict,
                })
            

    else:
        if method:
            initial_dict = {'method': method}
        else:
            initial_dict = {}

        form = GetRequestAPIForm(initial=initial_dict)

    template_context.update({
        'form': form, 
        'method': method,
        # 'example_form': example_form,
        # 'items': items
        # 'query_dict': query_dict,
        })

    # content_stream = render_to_string(template_name, template_context, context_instance=RequestContext(request))

    # return StreamingHttpResponse(streaming_content = content_stream)
    return render_to_response(template_name, template_context, context_instance=RequestContext(request))
