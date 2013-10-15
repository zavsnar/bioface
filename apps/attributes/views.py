# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import

from dateutil.parser import parse as datetime_parse

from django.http import Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.cache import cache

from apps.common.utils import api_request
from apps.attributes.forms import CreateAttributeForm, EditAttributeForm

@login_required
def attribute_list(request):
    organism_id = request.REQUEST.get('organism_id', '')

    if not organism_id:
        organisms = cache.get('organisms', [])
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
    if content_dict.has_key('result'):
        attr_list = content_dict['result']['attributes']

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
        rp = request.POST
        
        if form.is_valid():
            cd = form.cleaned_data
            atype = cd.get('atype')
            default_name = 'descr_{}_default'.format(atype)
            default_value = cd.get(default_name, None)
            if not default_value and default_value != 0:
                default_value = None
            primary = bool(rp.get('primary'))

            if atype == 'integer':
                description_dict = {'default': int(default_value) if default_value else default_value}
            elif atype == 'string':
                description_dict = {'default': default_value}
            elif atype == 'float':
                description_dict = {'default': float(default_value) if default_value else default_value}
            elif atype == 'nominal':
                nominal_list = cd.get('descr_nominal')
                description_dict = {"default": default_value, "items": nominal_list}
            elif atype == 'scale':
                scale_list=[]
                for i, scale in enumerate(cd.get('descr_scale')):
                    scale_list.append({'name': scale, 'weight': i*10})
                
                description_dict = {"default": default_value, "scale": scale_list}
            elif atype == 'range':
                description_dict = {
                    "default": default_value, 
                    "lower": cd.get('descr_range_from', ''), 
                    "upper": cd.get('descr_range_to', '')
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
                        "primary": primary,
                    }
                }
            }

            content_dict = api_request(query_dict)
            
            if content_dict.has_key('result'):
                cache.delete('attributes_{}'.format(cd['organism']))
                messages.success(request, 'Attribute {0} with ID {1} and Version {2} successfully created.'.format(
                    form.cleaned_data['name'], content_dict['result']['id'], content_dict['result']['version'])
                )
                return redirect('attributes')


            elif content_dict.has_key('error'):
                    messages.error(request, 'ERROR: {}'.format(content_dict['error']['message']))
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

            else:
                form = EditAttributeForm(request=request, data=rp)
                if form.is_valid():
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
        })
        attr_data['tags'] = ','.join(attr_data['tags'])
        form = EditAttributeForm(request=request, data=attr_data)
        template_context.update({
            'form': form,
        })
        
    elif content_dict.has_key('error'):
        messages.error(request, 'ERROR: {}'.format(content_dict['error']['data']))        

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
    