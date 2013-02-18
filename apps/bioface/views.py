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
from django.http import StreamingHttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from apps.bioface.utils import api_request
from apps.bioface.forms import add_update_segment_form, GetRequestAPIForm, RegistrationForm, QueryMethodForm

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
                    http_response, content_dict = api_request(query)

                    if not content_dict.has_key('error'):
                        sessionkey = content_dict['result']['key']

                        # Django login
                        login(request, user)
                        user.sessionkey = sessionkey
                        user.save()
                        messages.success(request, "You successfully logged.")
                        return redirect('/')
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
        redirect_url = request.GET.get('next') if request.GET.get('next', None) else '/'
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
    template_context = {}
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

@login_required
def request_api_page(request):
    response=''
    template_context={}
    template_name = "request_page.html"
    if request.method == 'POST':
        form = GetRequestAPIForm(data = request.POST)

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
            # if cd['limit'] or cd['skip']:
            #     query_dict['params'] = {}
            #     if cd['limit']:
            #         query_dict['params']['limit'] = cd['limit']
            #     if cd['skip']:
            #         query_dict['params']['skip'] = cd['skip']

            # print query_dict
            # query_dict['key'] = request.user.sessionkey
            page = request.GET.get('page', 1)
            template_name, template_context = get_pagination_page(page, query_dict)

            # http_response, content_dict = api_request(request, query_dict)
            # if not content_dict.has_key('error'):
            #     # item_name = query_dict['method'].replace('get_', '')
            #     # if query_dict['method'] in METHODS_FOR_CALL_ITEM:
            #     #     get_item_by_api()
            #     # # elif query_dict['method'] == "get_objects":
            #     # #     template_context = {
            #     # #         'attributes': content_dict['result']['attributes'],
            #     # #         'objects': content_dict['result']['objects']
            #     # #     }
            #     # elif query_dict['method'] in METHODS_FOR_CALL_ITEMS:
                    
            #     #     template_name, template_context = get_item_list_by_api(item_name, content_dict)


                
            # else:   
            #     msg = content_dict['error']['message']
            #     messages.error(request, 'API ERROR: {}'.format(msg)) 
            
            # template_context['response'] = content_dict

            # page = request.GET.get('page', 1)


            # paginator = Paginator(template_context['items'], 5) # Show 25 items per page

            # try:
            #     items = paginator.page(page)
            # except PageNotAnInteger:
            #     # If page is not an integer, deliver first page.
            #     items = paginator.page(1)
            # except EmptyPage:
            #     # If page is out of range (e.g. 9999), deliver last page of results.
            #     items = paginator.page(paginator.num_pages)

            # template_context['items'] = items

            template_context.update({
                'query_dict': query_dict,
                })
            

    else:
        form = GetRequestAPIForm()


    # from apps.bioface.forms import ExampleForm

    # example_form = ExampleForm()

    # from apps.bioface.ajax import get_pagination_page
    # page = request.GET.get('page')

    # if page:
    #     items = get_pagination_page(page)
    # else:
    #     # If page is not an integer, deliver first page.
    #     items = get_pagination_page(1)

    template_context.update({
        'form': form, 
        # 'example_form': example_form,
        # 'items': items
        # 'query_dict': query_dict,
        })

    # content_stream = render_to_string(template_name, template_context, context_instance=RequestContext(request))

    # return StreamingHttpResponse(streaming_content = content_stream)
    return render_to_response(template_name, template_context, context_instance=RequestContext(request))
