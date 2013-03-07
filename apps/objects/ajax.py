from __future__ import unicode_literals

import ast

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

# from apps.bioface.utils import ajax_login_required
from apps.bioface.forms import CreateOrganismForm, SelectObjects
from apps.bioface.utils import api_request, get_choices

def add_ajax_form(request, form, query_dict, html_selector):
    dajax = Dajax()
    if form.is_valid():
        # query_dict = {
        #   "method" : "add_organism",
        #   "key": request.user.sessionkey,
        #   "params" : {
        #       "data" : {
        #           "name": form.cleaned_data['name']
        #       }
        #   }
        # }

        http_response, content_dict = api_request(query_dict)
        if content_dict.has_key('result'):
            id = content_dict['result']['id']
            name = form.cleaned_data['name']
            dajax.script("success_adding('{0}', '{1}');".format(id, name))
        else:
            form._errors['name'] = ErrorList((content_dict['error']['message'],))
            # error_html = '<span class="help-inline">ERROR: {}</span>'.format(content_dict['error']['data'])
            # dajax.assign('#myModal1 #error_for_name', 'innerHTML', content_dict['error']['message'])
            # dajax.add_css_class('#myModal1 #error_for_name', 'error')
            # dajax.add_css_class('#myModal1 input#id_name', 'error')
     #        dajax.remove_css_class('#create_organism input', 'error')
     #        dajax.alert("Form is_valid(), your username is: %s" % form.cleaned_data.get('username'))
    # else:
        # dajax.add_css_class('#create_organism input', 'error')
        # for error in form.errors:
            # dajax.add_css_class('#myModal1 input#id_%s' % error, 'error')

    # render = form
    # dajax.assign('#create_organism', 'innerHTML', render)
    context = {'additional_form': form}
    context.update(csrf(request))
    render = render_to_string('create_organism.html', context)
    dajax.assign(html_selector, 'innerHTML', render)
    return dajax.json()


@dajaxice_register
def add_organism(request, form):
    form = CreateOrganismForm(deserialize_form(form))
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
    else:
        query_dict = {}

    return add_ajax_form(request = request, form=form, 
        query_dict=query_dict, html_selector='#create_organism')



@dajaxice_register
def update_attributes_from_organism(request, organism_id, form):
    form_data = deserialize_form(form)
    form = SelectObjects(request = request, data = deserialize_form(form))
    attr_field = form.fields['attributes_list']
    attr_list = get_choices(request, item_name='attributes', cache_key='attributes_{}'.format(organism_id), key='name', query="organism = {}".format(organism_id))
    attr_field.choices = attr_list
    value = form_data.getlist('attributes_list')
    render = attr_field.widget.render(name='attributes_list', value = value)

    options=[]
    for attr_name, attr_value in attr_list:
        options.append('<option value="attr.{0}">{1}</option>'.format(attr_name, attr_value))

    options_render = '\n'.join(options)
    # raise
    # query_dict = {
    #     "method" : method,
    #     "key": request.user.sessionkey,
    #     # "params" : {
    #     #     # "query" : "reference_id = id",
    #     #     "limit" : cd['limit'],
    #     #     "skip" : cd['skip'],
    #     #     # "orderby" : [["field_name", "acs"], ["field_name2", "desc"]]
    #     # }
    # }

    # template_name, template_context = get_pagination_page(page, query_dict)
    # render = render_to_string('result_list_paginated.html', template_context)

    dajax = Dajax()
    dajax.assign('#js_attribute_container div.controls', 'innerHTML', render)
    dajax.script('create_attribute_select();')
    dajax.assign('#js_reference_query_item .js_query_attr_list', 'innerHTML', options_render)
    dajax.script('update_query_items();')
    return dajax.json()

from apps.objects.views import get_pagination_page

@dajaxice_register
# @ajax_login_required
# def pagination(request, page, paginate_by, display_fields, attributes, row_query):
def pagination(request, page, paginate_by, data):
    
    data = ast.literal_eval(data)
    display_fields = data['display_fields']
    query_dict = data['query_dict']
    if query_dict['params'].has_key('attributes_list'):
        attributes = query_dict['params']['attributes_list']
    else:
        attributes = []

    content_dict = get_pagination_page(page=page, paginate_by=paginate_by, query_dict=query_dict)

    if content_dict.has_key('result'):
        object_list = []
        for obj in content_dict['result']['objects']:
            # for field in fields:
                # obj[field]
            object_list.append(
                {'object_name': obj['name'],
                'url': reverse('update_object', kwargs={'object_id': obj['id']}),
                'fields' :[ obj[field] for field in display_fields ],
                'attrs': [ obj['attributes'][attr] for attr in attributes ]
                }
            )

        if len(object_list) > paginate_by:
            next_page = True
            object_list = object_list[:-1]
        else:
            next_page = False

        previous_page = True if page > 1 else False

        query_dict_str = mark_safe(simplejson.dumps(query_dict))
        display_fields_str = mark_safe(simplejson.dumps(display_fields))
        template_context = {
            'has_next': next_page,
            'has_previous': previous_page,
            'next_page_number': page+1,
            'previous_page_number': page-1,
            'paginate_by': paginate_by,

            'display_fields': display_fields,
            'display_fields_str': display_fields_str,
            'attributes': attributes,
            'object_list': object_list,
            'query_dict_str': query_dict_str
        }


    render = render_to_string('object_pagination.html', template_context)

    dajax = Dajax()
    dajax.assign('#js_object_result_table', 'innerHTML', render)
    dajax.script('stop_show_loading();')
    return dajax.json()