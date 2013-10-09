from __future__ import unicode_literals, absolute_import, division

import math
from dateutil.parser import parse as datetime_parse
import ast
import json

from dajax.core import Dajax
from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from dajaxice.utils import deserialize_form

from django.contrib.auth.decorators import login_required
from django.forms.util import ErrorList
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.db import IntegrityError

from apps.objects.views import get_pagination_page
from apps.objects.forms import CreateOrganismForm, SelectObjects
from apps.persons.models import SavedQuery, Download
from apps.common.utils import api_request, get_choices

##### For page Select Objects #####

@dajaxice_register
def update_attr_from_tag(request, organism, tag, attrs):
    query_dict = {
        "method" : "get_attributes",
        "key": request.user.sessionkey,
        "params" : {
            'query' : 'organism = {0} & tags.contains("{1}")'.format(organism, tag),
        }
    }
    content_dict = api_request(query_dict)
    dajax = Dajax()
    if content_dict.has_key('result'):
        new_attrs = [ attr['name'] for attr in content_dict['result']['attributes'] ]
        if new_attrs:
            attrs.extend(new_attrs)
            result_attr_list = attrs
            dajax.add_data(result_attr_list, 'update_attr_from_tag')
    else:
        template_context = {'error_message': 'Error. {}.'.format(content_dict['error']['message'])}
        render = render_to_string('components/alert_messages.html', template_context)
        dajax.assign('.extra-message-block', 'innerHTML', render)

    return dajax.json()


@dajaxice_register
def update_attributes_from_organism(request, organism_id):
    query_params = {
        "query": "organism = {}".format(organism_id),
        "orderby" : [["name", "asc"]]
    }
    attr_list = get_choices(request, item_name='attributes', cache_key='attributes_{}'.format(organism_id), 
        key='name', query_params=query_params, append_field = 'atype')

    attr_render = '<select multiple="multiple" id="id_attributes_list" name="attributes_list" style="width:530px">\n'
    options=[]
    for attr_name, attr_value, atype in attr_list:
        attr_render = attr_render + '<option value="{0}">{1}</option>\n'.format(attr_name, attr_value)
        options.append('<option value="attr.{0}" data-atype="{2}">{1}</option>'.format(attr_name, attr_value, atype))
    
    attr_render = attr_render + '</select>\n'
    options_render = '\n'.join(options)

    dajax = Dajax()
    dajax.assign('#js_attribute_container div.controls', 'innerHTML', attr_render)
    dajax.assign('#js_sort_by_container div.controls', 'innerHTML', attr_render)
    dajax.script('create_attribute_select();')
    dajax.assign('#js_reference_query_item .js_query_attr_list', 'innerHTML', options_render)
    dajax.script('update_query_items();')
    return dajax.json()


@dajaxice_register
def save_query(request, name, form, field_filters_dict, query_str):
    dajax = Dajax()
    form_data = deserialize_form(form)
    organism = form_data.get('organism')
    display_fields = form_data.getlist('display_fields')
    attributes_list = form_data.getlist('attributes_list')
    paginate_by = form_data.get('paginate_by')
    sort_by = form_data.get('sort_by')
    try:
        saved_query = SavedQuery.objects.create(
            type_query = 'get_objects',
            name = name,
            user = request.user, 
            organism_id = organism,
            display_fields = display_fields,
            attributes_list = attributes_list,
            filter_fields = field_filters_dict,
            query_str = query_str,
            paginate_by = paginate_by,
            sort_by = sort_by
        )
        query_item = render_to_string('saved_query_components.html', {'query': saved_query})
        dajax.append('.js_query_list', 'innerHTML', query_item)
        template_context = {'success_message': 'Query "{}" successfully saved.'.format(name)}
        dajax.script('save_query_success();')
    except IntegrityError:
        template_context = {'error_message': 'Name for query must be unique!'}
        dajax.script('save_query_error();')

    message_body = render_to_string('components/alert_messages.html', template_context)
    dajax.assign('.extra-message-block', 'innerHTML', message_body)
    dajax.script('show_messages();')
    dajax.script('stop_show_loading();')
    
    return dajax.json()
    

@dajaxice_register
def delete_saved_query(request, name):
    try:
        query = SavedQuery.objects.get(user = request.user, name = name)
        query.delete()
        template_context = {'success_message': 'Query "{}" successfully deleted.'.format(name)}
    except SavedQuery.DoesNotExist:
        template_context = {'error_message': 'Query does not exist.'}

    dajax = Dajax()
    render = render_to_string('components/alert_messages.html', template_context)
    dajax.assign('.extra-message-block', 'innerHTML', render)
    dajax.script('stop_show_loading();')
    return dajax.json()


@dajaxice_register
def tagging_objects(request, page_num, tags, query_dict):
    query_dict = json.loads(query_dict)
    
    query_dict['params']['count'] = False
    if query_dict['params'].has_key('skip'):
        del query_dict['params']['skip']
    if query_dict['params'].has_key('limit'):
        del query_dict['params']['limit']
    content_dict = api_request(query_dict)
    dajax = Dajax()

    if content_dict.has_key('result'):
        obj_id_list = [ obj['id'] for obj in content_dict['result']['objects'] ]
        tags = json.loads(tags)
        for obj_id in obj_id_list:
            tag_query = { 
                "method": "tag_object",
                "key": request.user.sessionkey,
                "params": {
                    "id": int(obj_id),
                    "tags": tags
                }
            }
            tag_content_dict = api_request(tag_query)
            if tag_content_dict.has_key('result'):
                template_context = {'success_message': 'Objects tagged'}
                dajax.script('get_page({});'.format(page_num))
            else:
                template_context = {'error_message': 'ERROR: {}'.format(tag_content_dict['error']['message'])}
    else:
        template_context = {'error_message': 'ERROR: {}'.format(content_dict['error']['message'])}

    render = render_to_string('components/alert_messages.html', template_context)
    dajax.assign('.extra-message-block', 'innerHTML', render)
    dajax.script('stop_show_loading();')
    return dajax.json()

@dajaxice_register
def download_objects(request, form, query_dict):
    dajax = Dajax()
    query_dict = ast.literal_eval(query_dict)
    form_data = deserialize_form(form)
    form = DownloadForm(data = form_data)
    if form.is_valid():
        del query_dict['params']['limit']
        del query_dict['params']['skip']

        encoding = form.cleaned_data['encoding']
        object_download = Download.objects.create(
            encoding = encoding,
            user = request.user,
            description = form.cleaned_data['description'],
            status = 'expected')

        with_attributes = True if 'attributes' in form.cleaned_data['options'] else False
        with_sequences = True if 'sequences' in form.cleaned_data['options'] else False
        obj_id = object_download.id
        # Add to queue
        download_task = loading_objects.delay(
            query_dict = query_dict, 
            object_download_id = obj_id,
            with_attributes = with_attributes,
            with_sequences = with_sequences,
            encoding = encoding
            )
        object_download.task_id = download_task.task_id
        object_download.save()

        msg = 'Ok'
        template_context = {'success_message': 'Downloading successfully begin. You can see the status or get file in "My downloads".'}
        dajax.script('success_adding_download();')
    else:
        msg = 'err'
    
    render = render_to_string('components/alert_messages.html', template_context)
    dajax.assign('.extra-message-block', 'innerHTML', render)
    
    return dajax.json()

@dajaxice_register
def pagination(request, page, paginate_by, items_count, data):
    data = json.loads(data)
    display_fields = data['display_fields']
    query_dict = data['query_dict']
    query_dict['params']['count'] = False
    if query_dict['params'].has_key('attributes_list'):
        attributes = [ attr for attr in query_dict['params']['attributes_list'] ]
    else:
        attributes = []

    content_dict = get_pagination_page(page=page, paginate_by=paginate_by, query_dict=query_dict)
    if content_dict.has_key('result'):
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
                object_attrs = [ None for i in attributes ]
                for obj_attr in obj['attributes']:
                    attr_index = attributes.index(obj_attr['name'])
                    object_attrs[attr_index] = obj_attr
            else:
                object_attrs = []

            object_list.append(
                {'object_name': obj['name'],
                'url': reverse('update_object', kwargs={'object_id': obj['id']}),
                'fields': object_fields,
                'attrs': object_attrs
                }
            )

        next_page = True if paginate_by * page < items_count else False
        previous_page = True if page > 1 else False

        pages_count = int(math.ceil(items_count/paginate_by))
        if pages_count <= 11:
            pages = range(1, pages_count+1)
        elif page == 1 or page == pages_count:
            pages = range(1, 4)
            pages.append('...')
            pages.extend(range(pages_count-2, pages_count+1))
        elif 1 < page <= 6:
            # page in begin
            pages = range(1, page+2)
            pages.append('...')
            pages.extend(range(pages_count-2, pages_count+1))
        elif pages_count-5 <= page < pages_count:
            # page in end
            pages = range(1, 4)
            pages.append('...')
            pages.extend(range(page-1, pages_count+1))
        else:
            # page in middle
            pages = range(1, 4)
            pages.append('...')
            pages.extend(range(page-1, page+2))
            pages.append('...')
            pages.extend(range(pages_count-2, pages_count+1))

        query_dict_str = mark_safe(simplejson.dumps(query_dict))
        display_fields_str = mark_safe(simplejson.dumps(display_fields))
        template_context = {
            'has_next': next_page,
            'has_previous': previous_page,
            'next_page_number': page+1,
            'previous_page_number': page-1,
            'paginate_by': paginate_by,
            'pages': pages,
            'this_page': page,
            'items_count': items_count,

            'display_fields': display_fields,
            'display_fields_str': display_fields_str,
            'attributes': attributes,
            'object_list': object_list,
            'query_dict_str': query_dict_str
        }

    render = render_to_string('object_list.html', template_context)

    dajax = Dajax()
    dajax.assign('#js_object_result_table', 'innerHTML', render)
    dajax.script('stop_show_loading();')
    return dajax.json()