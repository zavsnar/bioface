# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# from __future__ import print_function
from __future__ import absolute_import

import urllib
import httplib2 
import json

import ast

from django import forms
from django.template import RequestContext
from django.shortcuts import render, render_to_response
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms.forms import NON_FIELD_ERRORS
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout as auth_logout
# from django.contrib.auth.views import login, logout
from django.contrib.auth.models import User
from django.views.generic import CreateView
from django.contrib import messages

# from apps.tasks.models import Task

METHODS_FOR_CALL_ITEM = ("get_object", "get_attribute", "get_tag", "get_tags_version", "get_sequence", "get_reference",
    "get_segment", "get_alignment", "get_annotation")
METHODS_FOR_CALL_ITEMS = ("get_attributes", "get_tags", "get_sequences", "get_references", 
    "get_segments", "get_alignments", "get_annotations", "get_objects")


def api_request(request, query_dict):
    API_URL = 'https://10.0.1.204:5000/api/v1/'
    headers = {'Content-type': 'application/json'}
    http = httplib2.Http(disable_ssl_certificate_validation=True)

    http_response, content = http.request(API_URL, 'POST', body = json.dumps(query_dict), headers = headers)
    content_dict = json.loads(content)

    return http_response, content_dict

class RegistrationForm(UserCreationForm):
    username = forms.EmailField(label="E-mail", max_length=70)

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
                    http_response, content_dict = api_request(request, query)

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
                        # form._errors[NON_FIELD_ERRORS] = form.error_class( (msg,))
                        
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

METHOD_CHOISES = zip(METHODS_FOR_CALL_ITEMS, METHODS_FOR_CALL_ITEMS)
# METHOD_CHOISES.append(("get_objects", "get_objects"))

class GetRequestAPIForm(forms.Form):
    request = forms.CharField(widget=forms.Textarea, required=False)
    method = forms.ChoiceField(choices = METHOD_CHOISES)
    row_query = forms.CharField(required=False)
    limit = forms.IntegerField(required=False)
    skip = forms.IntegerField(required=False)


def get_item_by_api():
    template_name = 'item_detail.html'


def get_item_list_by_api(item_name, content_dict):
    

    template_name = 'item_list.html'
    template_context = {}
    item_list = content_dict['result'].get(item_name, None)
    if item_list:
        if item_name == "objects1":
            attr_name_list = [ attr['name'] for attr in content_dict['result']['attributes'] ]
            print attr_name_list
        else:
            attr_name_list = set([param_name for item in item_list for param_name in item.keys()])

        template_context = {'attr_name_list': attr_name_list, 'item_name': item_name, 'items': item_list}

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
            if cd['limit'] or cd['skip']:
                query_dict['params'] = {}
                if cd['limit']:
                    query_dict['params']['limit'] = cd['limit']
                if cd['skip']:
                    query_dict['params']['skip'] = cd['skip']

            # print query_dict
            # query_dict['key'] = request.user.sessionkey
            http_response, content_dict = api_request(request, query_dict)
            if not content_dict.has_key('error'):
                item_name = query_dict['method'].replace('get_', '')
                if query_dict['method'] in METHODS_FOR_CALL_ITEM:
                    get_item_by_api()
                # elif query_dict['method'] == "get_objects":
                #     template_context = {
                #         'attributes': content_dict['result']['attributes'],
                #         'objects': content_dict['result']['objects']
                #     }
                elif query_dict['method'] in METHODS_FOR_CALL_ITEMS:
                    
                    template_name, template_context = get_item_list_by_api(item_name, content_dict)
                

            else:   
                msg = content_dict['error']['message']
                messages.error(request, 'API ERROR: {}'.format(msg)) 
            
            
            template_context['response'] = content_dict
                        
    else:
        form = GetRequestAPIForm()

    template_context.update({
        'form': form, 
        })
    return render_to_response(template_name, template_context, context_instance=RequestContext(request))
