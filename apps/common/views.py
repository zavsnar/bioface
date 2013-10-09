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
from django.contrib.auth import get_user_model, authenticate, login, logout as auth_logout
from django.contrib import messages
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from apps.common.utils import api_request, API_URL
from apps.common.forms import *


def index(request):
    # TODO design index page
    # temporal redirect
    return redirect('select_objects')

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        query = {
            "method" : "login",
            "params" : {
                "email": username,
                "password": password
                }
            }

        # Login in service by API
        content_dict = api_request(query)

        if not content_dict.has_key('error'):
            user = authenticate(username=username, password=password)
            if not user or not user.is_active:
                #  user exist in back-end server, and not exist in our DB
                form = AuthenticationForm(data = request.POST)
                user_model = get_user_model()
                user_model.objects.create_user(username, email=username, password=password)
                user = authenticate(username=username, password=password)

            sessionkey = content_dict['result']['key']
            # Django login
            login(request, user)
            user.sessionkey = sessionkey
            user.save()
            messages.success(request, "You successfully logged.")
            redirect_url = request.GET.get('next') if request.GET.get('next', None) else '/'
            return redirect(redirect_url)
        else:
            msg = content_dict['error']['message']
            messages.error(request, msg)
            form = AuthenticationForm(data = request.POST) 
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
            new_user = authenticate(username=request.POST['username'],
                                    password=request.POST['password1'])
            auth_login(request, new_user)
            return redirect("/")
    else:
        form = RegistrationForm()

    return render_to_response("registration.html", {'form': form},
        context_instance=RequestContext(request))


@login_required
def create_organism(request):
    if request.method == 'POST':
        form = CreateOrganismForm(data = request.POST)
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

            content_dict = api_request(query_dict)
            
            if content_dict.has_key('result'):
                cache.delete('organisms')
                messages.success(request, 'Organism "{}" successfully create.'.format(form.cleaned_data['name']))
            elif content_dict.has_key('error'):
                messages.error(request, 'ERROR: {}'.format(content_dict['error']['message']))

    else:
        form = CreateOrganismForm()

    template_context = {'form': form,}
    return render_to_response('create_organism.html', template_context, context_instance=RequestContext(request))


def get_pagination_page(page, query_dict):
    item_count = 5
    item_name = query_dict['method'].replace('get_', '')
    if not query_dict.has_key('params'):
        query_dict['params'] = {}

    # Monkey patch. Need for test existing next page
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