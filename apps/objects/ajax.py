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

# from apps.bioface.utils import ajax_login_required
from apps.objects.views import get_pagination_page
from apps.objects.forms import CreateOrganismForm, SelectObjects
from apps.bioface.models import SavedQuery
from apps.bioface.utils import api_request, get_choices

@dajaxice_register
def update_attributes_from_organism(request, organism_id):
    # form_data = deserialize_form(form)
    # form = SelectObjects(request=request, data=deserialize_form(form), with_choices=False)
    # attr_field = form.fields['attributes_list']
    attr_list = get_choices(request, item_name='attributes', cache_key='attributes_{}'.format(organism_id), 
        key='name', query="organism = {}".format(organism_id), append_field = 'atype')
    # attr_field.choices = attr_list
    # value = form_data.getlist('attributes_list')
    # render = attr_field.widget.render(name='attributes_list', value = value)

    attr_render = '<select multiple="multiple" id="id_attributes_list" name="attributes_list" style="width:530px">\n'
    options=[]
    for attr_name, attr_value, atype in attr_list:
        attr_render = attr_render + '<option value="{0}">{1}</option>\n'.format(attr_name, attr_value)
        options.append('<option value="attr.{0}" data-atype="{2}">{1}</option>'.format(attr_name, attr_value, atype))
    
    attr_render = attr_render + '</select>\n'
    options_render = '\n'.join(options)

    dajax = Dajax()
    dajax.assign('#js_attribute_container div.controls', 'innerHTML', attr_render)
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
        query = SavedQuery.objects.get(user = request.user, 
            # type_query = 'get_objects', 
            name = name)
        query.delete()
        template_context = {'success_message': 'Query "{}" successfully deleted.'.format(name)}
    except SavedQuery.DoesNotExist:
        template_context = {'error_message': 'Query does not exist.'}

    dajax = Dajax()
    # dajax.alert('Success! {}'.format(saved_query))
    render = render_to_string('components/alert_messages.html', template_context)
    dajax.assign('.extra-message-block', 'innerHTML', render)
    dajax.script('stop_show_loading();')
    return dajax.json()

@dajaxice_register
# @ajax_login_required
# def pagination(request, page, paginate_by, display_fields, attributes, raw_query):
def pagination(request, page, paginate_by, items_count, data):
    # data = ast.literal_eval(data)
    data = json.loads(data)
    display_fields = data['display_fields']
    query_dict = data['query_dict']
    query_dict['params']['count'] = False
    if query_dict['params'].has_key('attributes_list'):
        attributes = [ attr for attr in query_dict['params']['attributes_list'] ]
    else:
        attributes = []

    content_dict = get_pagination_page(page=page, paginate_by=paginate_by, query_dict=query_dict)
    # print 777, content_dict['result']['objects']
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
        # all_pages = range(1, pages_count+1)
        if pages_count == 11:
            pages = range(1, 12)
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

        # if len(object_list) > paginate_by:
        #     next_page = True
        #     object_list = object_list[:-1]
        # else:
        #     next_page = False


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