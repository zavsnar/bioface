from __future__ import unicode_literals
# from __future__ import print_function
from __future__ import absolute_import

from django import forms
from django.core.cache import cache
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from django_select2 import *
from django_select2.widgets import *

from apps.bioface.utils import api_request, get_choices

METHODS_FOR_CALL_ITEM = ("get_object", "get_attribute", "get_tag", "get_tags_version", "get_sequence", "get_reference",
    "get_segment", "get_alignment", "get_annotation")
METHODS_FOR_CALL_ITEMS = ("get_attributes", "get_tags", "get_sequences", "get_references", 
    "get_segments", "get_alignments", "get_annotations", "get_objects")

METHODS_FOR_CREATE_ITEM = ("add_segment", "add_object")

CREATE_METHOD_CHOISES = [ (i, i.replace('add_', '')) for i in METHODS_FOR_CREATE_ITEM ]

GET_METHOD_CHOISES = zip(METHODS_FOR_CALL_ITEMS, METHODS_FOR_CALL_ITEMS)
# METHOD_CHOISES.append(("get_objects", "get_objects"))

class GetRequestAPIForm(forms.Form):
    # request = forms.CharField(widget=forms.Textarea, required=False)
    method = forms.ChoiceField(choices = GET_METHOD_CHOISES)
    # row_query = forms.CharField(required=False)
    # limit = forms.IntegerField(required=False)
    # skip = forms.IntegerField(required=False)

OBJECT_FIELDS = ('comment', 'lab_id', 'user_id', 'created', 'creator', 'modified', 'source', 'organism', 'id', 'version')
OBJECT_FIELDS_CHOICES = zip(OBJECT_FIELDS, OBJECT_FIELDS)


class SelectObjects(forms.Form):
    # request = forms.CharField(widget=forms.Textarea, required=False)
    # method = forms.ChoiceField(choices = GET_METHOD_CHOISES, initial = 'get_objects')
    organism = forms.ChoiceField(widget=forms.Select(attrs={'style': 'width:220px'}))
    display_fields = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple(), choices=OBJECT_FIELDS_CHOICES, initial=('name',))
    attributes_list = forms.MultipleChoiceField(required=False, widget=forms.SelectMultiple(attrs={'style': 'width:220px'}))
    
    # row_query = forms.CharField(required=False)
    # limit = forms.IntegerField(required=False)
    # skip = forms.IntegerField(required=False)

    def __init__(self, request, *args, **kwargs):
        super(SelectObjects, self).__init__(*args, **kwargs)
        self.request = request
        self.fields['attributes_list'].choices = get_choices(request, item_name='attributes', key='name')
        choices_list = [('', '')]
        choices_list.extend(get_choices(request, item_name='organisms'))
        self.fields['organism'].choices = choices_list

    def clean(self):
        if self.cleaned_data.has_key('organism') and self.cleaned_data['organism']:
            organism_id = self.cleaned_data['organism']
            attr_field = self.fields['attributes_list']
            attr_list = get_choices(self.request, cache_key='attributes_{}'.format(organism_id), item_name='attributes', key='name', query="organism = {}".format(organism_id))
            attr_field.choices = attr_list
        return self.cleaned_data

class QueryMethodForm(forms.Form):
        method = forms.MultipleChoiceField(label='Add', choices=CREATE_METHOD_CHOISES, 
            required=False, widget=forms.SelectMultiple(attrs={'style': 'width:220px', 'class': 'select_method'}))

class CreateOrganismForm(forms.Form):
    name = forms.CharField(label='Name')

class TagMixin(forms.Form):
    tags = forms.CharField(label = 'Tag', required=False, widget=forms.TextInput(attrs={'style': 'width:220px'}))

    def __init__(self, request, *args, **kwargs):
        super(TagMixin, self).__init__(*args, **kwargs)
        self.request = request
        self.fields['tags'].choices = get_choices(request, item_name='tags')

    def clean_tags(self):
        tags=[]
        new_tags=[]
        for tag in self.cleaned_data['tags'].split(','):
            tag_exist = False
            for id, name in self.fields['tags'].choices:
                if tag == name:
                    tags.append(id)
                    tag_exist = True
                    break

            if not tag_exist:
                query_dict = {
                    "method": "add_tag",
                    "key": self.request.user.sessionkey,
                    "params": {"data": {"tag": tag}}
                }

                http_response, content_dict = api_request(query_dict)
                if content_dict['result']:
                    new_tags.append(content_dict['result']['id'])

        tags.extend(new_tags)

        if new_tags:
            self.fields['tags'].choices = get_choices(self.request, item_name='tags')

        self.cleaned_data['tags'] = tags
        return self.cleaned_data['tags']



# def create_object_form(request, *args, **kwargs):
class CreateObjectForm(TagMixin):
    name = forms.CharField(label='Name')
    lab_id = forms.CharField(label='laboratory ID', required=False)
    # tags = forms.CharField(required=False)
    organism = forms.ChoiceField(widget=forms.Select(attrs={'style': 'width:220px'}))
    source = forms.CharField(required=False)
    comment = forms.CharField(required=False)

    def __init__(self, request, *args, **kwargs):
        super(CreateObjectForm, self).__init__(request, *args, **kwargs)
        self.request = request
        self.fields['organism'].choices = get_choices(request, item_name='organisms')
        # self.fields['tags'].choices = get_choices(request, item_name='tags')

    # def clean_tags(self):
    #     tags=[]
    #     new_tags=[]
    #     for tag in self.cleaned_data['tags'].split(','):
    #         tag_exist = False
    #         for id, name in self.fields['tags'].choices:
    #             if tag == name:
    #                 tags.append(id)
    #                 tag_exist = True
    #                 break

    #         if not tag_exist:
    #             query_dict = {
    #                 "method": "add_tag",
    #                 "key": self.request.user.sessionkey,
    #                 "params": {
    #                     "data": {
    #                         "tag": tag
    #                     }
    #                 }
    #             }

    #             http_response, content_dict = api_request(query_dict)
    #             print 5555, content_dict
    #             if content_dict['result']:
    #                 new_tags.append(content_dict['result']['id'])

    #     tags.extend(new_tags)

    #     if new_tags:
    #         self.fields['tags'].choices = get_choices(self.request, item_name='tags')

    #     self.cleaned_data['tags'] = tags
    #     print 7777, self.cleaned_data['tags']
    #     return self.cleaned_data['tags']
    # return CreateObjectForm(*args, **kwargs)


class UpdateObjectForm(CreateObjectForm):
    id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    version = forms.IntegerField(widget=forms.HiddenInput, required=False)
    # sequences = forms.ComboField(fields=[forms.CharField(max_length=20), forms.EmailField()])

    def __init__(self, request, *args, **kwargs):
        super(UpdateObjectForm, self).__init__(request, *args, **kwargs)
