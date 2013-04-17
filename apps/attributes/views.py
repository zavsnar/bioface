# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# from __future__ import print_function
from __future__ import absolute_import

# import urllib
# import httplib2 
# import json

from dateutil.parser import parse as datetime_parse

# import ast

# from django.conf import settings
# from django import forms
# from django.forms.formsets import formset_factory
from django.http import Http404
from django.template import RequestContext
# from django.template.loader import render_to_string
from django.shortcuts import render_to_response, redirect
# from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
# from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib import messages
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache



from apps.bioface.utils import api_request
from apps.attributes.forms import CreateAttributeForm, EditAttributeForm

@login_required
def attribute_list(request):
    organism_id = request.REQUEST.get('organism_id', '')

    if not organism_id:
        organisms = cache.get('organisms', [])
        print 1111, organisms
        if organisms:
            organism_id = organisms[0][0]
        else:
            query_organism = {
                "method" : "get_organisms",
                "key": request.user.sessionkey,
            }
            organisms_dict = api_request(query_organism)

            try:
                organism_id = organisms_dict['result']['organisms'][0]['id']
            except KeyError:
                if organisms_dict.has_key('error'):
                    msg = organisms_dict['error']['message']
                    messages.error(request, 'API ERROR: {}. {}'.format(msg, organisms_dict['error']['data']))
                else:
                    raise Http404

    print organism_id            
    query_dict = {
        "method" : "get_attributes",
        "key": request.user.sessionkey,
        "params" : {
            "query" : "organism = {}".format(organism_id),
            # "limit" : int,
            # "skip" : int,
            "orderby" : [["name", "asc"]]
        }
    }

    content_dict = api_request(query_dict)
    # {"user_id": 331, "name": "Аналитик", "creator": 331, 
    # "created": "2013-04-02T16:58:04.183092+04:00", "atype": "nominal", 
    # "modified": "2013-04-02T16:58:04.183092+04:00", 
    # "primary": false, "version": 5060860, "organism": 302, 
    # "id": 27277, 
    # "description": {"default": "AAA", 
    # "items": ["AAA", "BBB", "GGG", "JJJ", "EEE", "FFF", "HHH", "III", "CCC", "DDD"]}}

    if content_dict.has_key('result'):
        attr_list = content_dict['result']['attributes']
        # result_list = []
        # for attr in attr_list:
        #     attr_dict = {
        #         'name': attr['name'],
        #         'atype': attr['atype'],
        #         'primary': attr['primary']
        #     }
        #     for time_field in ('created', 'modified'):
        #         time_value = datetime_parse(attr[time_field])
        #         field_value = time_value.strftime("%Y-%m-%d %H:%M:%S")
        #         attr_dict[time_field] = field_value

        #     if attr['atype'] 

        for attr in attr_list:
            time_value = datetime_parse(attr['created'])
            attr['created'] = time_value.strftime("%Y-%m-%d %H:%M:%S")

        template_context = {'item_list': attr_list}
    else:
        template_context ={}
        msg = content_dict['error']['message']
        messages.error(request, 'API ERROR: {}. {}'.format(msg, content_dict['error']['data']))
        


    return render_to_response("attribute_list.html", template_context, context_instance=RequestContext(request))

@login_required
def create_attribute(request):
    description_errors=[]
    if request.method == 'POST':
        form = CreateAttributeForm(request = request, data = request.POST)
        # print 2222, request.POST['descr-nominal']
        rp = request.POST
        
        if form.is_valid():
            cd = form.cleaned_data
            atype = cd.get('atype')
            default_name = 'descr_{}_default'.format(atype)
            default_value = cd.get(default_name, None)
            if not default_value:
                default_value = None
            primary = bool(rp.get('primary'))
            print 333, default_value
            # raise

            if atype == 'integer':
                #  27303
                #  27308
                description_dict = {'default': int(default_value) if default_value else default_value}
            elif atype == 'string':
                description_dict = {'default': default_value}
            elif atype == 'float':
                description_dict = {'default': float(default_value) if default_value else default_value}
            elif atype == 'nominal':
                # default_value = rp.get('descr-nominal-default')
                nominal_list = cd.get('descr_nominal')
                description_dict = {"default": default_value, "items": nominal_list}
            elif atype == 'scale':
                # default_value = rp.get('descr-{}-default'.format(atype))
                
                # {"default": str, "scale": [{name: str, weight: int},...]}
                scale_list=[]
                for i, scale in enumerate(cd.get('descr_scale')):
                    scale_list.append({'name': scale, 'weight': i*10})
                
                # for _l in cd.get('descr_{}'.format(atype)).split('; '):
                #     name, weight = _l.split(', ')
                #     scale_list.append({'name': name, 'weight': int(weight)})

                description_dict = {"default": default_value, "scale": scale_list}
                # scale_dict = map(lambda x: x.split(', '), rp.get('descr-nominal').split('; '))
            elif atype == 'range':
                description_dict = {
                    "default": default_value, 
                    "upper": cd.get('descr_range_from', ''), 
                    "lower": cd.get('descr_range_to', '')
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

            content_dict = api_request(query_dict)
            
            if content_dict.has_key('result'):
            # {u'error': {u'code': -32005,
            # u'data': u'(IntegrityError) duplicate key value violates unique constraint "objects_name_key"\nDETAIL:  Key (name)=(123) already exists.\n',
            # u'message': u'not unique'}}
                cache.delete('attributes_{}'.format(cd['organism']))
                messages.success(request, 'Attribute {0} with ID {1} and Version {2} successfully created.'.format(
                    form.cleaned_data['name'], content_dict['result']['id'], content_dict['result']['version'])
                )
                return redirect('attributes')


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
    return render_to_response('create_attribute.html', template_context, 
        context_instance=RequestContext(request))

@login_required
def edit_attribute(request, attr_id):
    template_context = {}
    if request.method == 'POST':
        rp = request.POST
        if rp.get('id', None) and rp.get('version', None):
            attr_id = int(rp.get('id'))
            attr_version = int(rp.get('version'))

            if rp.get('is_delete', None):
                success = delete_attribute(request=request, id=attr_id, version=attr_version)
                if success:
                    return redirect('attributes')

            elif rp.get('name', None):
                form = EditAttributeForm(request)
                query_dict = {
                    "method" : "update_attribute",
                    "key": request.user.sessionkey,
                    "params" : {
                        "id" : attr_id,
                        "version": attr_version,
                        "data": { "name": rp['name'] }
                    }
                }

                content_dict = api_request(query_dict)
                
                if content_dict.has_key('result'):
                    messages.success(request, 'Attribute change.')
                    cache.delete('attributes')
                elif content_dict.has_key('error'):
                        messages.error(request, 'ERROR: {}'.format(content_dict['error']['data']))
    # else:
    query_dict = {
        "method" : "get_attribute",
        "key": request.user.sessionkey,
        "params" : {
            "id" : int(attr_id)
        }
    }

    content_dict = api_request(query_dict)
    if content_dict.has_key('result'):
        attr_data = content_dict['result']['attribute']
        template_context.update({
            'id': attr_data['id'],
            'version': attr_data['version'],
            'name': attr_data['name'],
            'atype': attr_data['atype'],
            'description': attr_data['description'],
            # 'attr_dict': attr_dict,
            # 'descr_{}_default'.format(attr_data['atype']): attr_data['description']['default']
        })

        form = EditAttributeForm(request=request, data=attr_data)
        template_context.update({
            'form': form,
        })
        # query_dict = {
        #     "method" : "get_organism",
        #     "key": request.user.sessionkey,
        #     "params" : {
        #         "id" : int(attr_data['organism'])
        #     }
        # }
        # content_dict = api_request(query_dict)
        # if content_dict.has_key('result'):
        #     template_context.update({
        #         'organism': content_dict['result']['organism']['name']
        #     })
        # elif content_dict.has_key('error'):
        #     messages.error(request, 'ERROR: {}'.format(content_dict['error']['data']))  
        
    elif content_dict.has_key('error'):
        messages.error(request, 'ERROR: {}'.format(content_dict['error']['data']))        

            # form = CreateAttributeForm(request = request)

    # template_context.update({
    #     'form': form,
        # 'description_errors': description_errors,
    # })
    return render_to_response('edit_attribute.html', template_context, 
        context_instance=RequestContext(request))


def delete_attribute(request, id, version):
    query_dict = {
        "method" : "delete_attribute",
        "key": request.user.sessionkey,
        "params" : {
            "id" : id,
            "version" : version
        }
    }
    content_dict = api_request(query_dict)
    
    if content_dict.has_key('result'):
        messages.success(request, 'Attribute delete.')
        cache.delete('attributes')
        success = True

    elif content_dict.has_key('error'):
        messages.error(request, 'ERROR: {}'.format(content_dict['error']['data']))
        success = False

    return success


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