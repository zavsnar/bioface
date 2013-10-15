# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import

from django.shortcuts import render_to_response, redirect
from django.contrib import messages

from apps.common.utils import api_request
from apps.sequences.forms import CreateSequenceForm

def create_sequence(request, sequence_id=None):
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

            content_dict = api_request(query_dict)
            
            if content_dict.has_key('result'):
                messages.success(request, 
                    'Object {0} with ID {1} and Version {2} successfully created.'.format(
                    form.cleaned_data['name'], content_dict['result']['id'], 
                    content_dict['result']['version'])
                )
                return redirect('update_object')
            elif content_dict.has_key('error'):
                messages.error(request, 'ERROR: {}'.format(content_dict['error']['data']))

    if sequence_id:
        query_dict = {
                "method" : "get_sequences",
                "key": request.user.sessionkey,
                "params" : {
                    "id" : sequence_id
            }
        }

        content_dict = api_request(query_dict)
        if content_dict.has_key('result'):
            form = CreateSequenceForm(request=request, initial=content_dict['result']['sequence'])
        elif content_dict.has_key('error'):
            messages.error(request, 'ERROR: {}'.format(content_dict['error']['data']))
    else:
        form = CreateSequenceForm(request=request)

    template_context = {
        'form': form,
    }
    return render_to_response('create_sequence.html', template_context, context_instance=RequestContext(request))


def sequence_list(request):
    template_context={}
    query_dict = {
            "method" : "get_sequences",
            "key": request.user.sessionkey,
            "params" : {
                "orderby" : [["name", "asc"]]
        }
    }

    content_dict = api_request(query_dict)

    if content_dict.has_key('result'):
        template_context.update({
            'sequences': content_dict['result']['sequences']
        })
    elif content_dict.has_key('error'):
        messages.error(request, 'ERROR: {}'.format(content_dict['error']['data']))

    return render_to_response('sequence_list.html', template_context, context_instance=RequestContext(request))
