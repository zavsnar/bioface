from __future__ import unicode_literals
# from __future__ import print_function
from __future__ import absolute_import

from django import forms
from django.utils.encoding import force_text



#from django_select2 import *
#from django_select2.widgets import *

from apps.bioface.utils import get_choices
from apps.bioface.forms import TagMixin

METHODS_FOR_CALL_ITEM = ("get_object", "get_attribute", "get_tag", "get_tags_version", "get_sequence", "get_reference",
    "get_segment", "get_alignment", "get_annotation")

METHODS_FOR_CREATE_ITEM = ("add_segment", "add_object")

CREATE_METHOD_CHOISES = [ (i, i.replace('add_', '')) for i in METHODS_FOR_CREATE_ITEM ]

OBJECT_FIELDS = ['name', 'comment', 'lab_id', 'user_id', 'created', 'creator', 'modified', \
    'source', 'organism', 'id']
DISPLAY_FIELDS = list(OBJECT_FIELDS)
DISPLAY_FIELDS.append('tags')
# OBJECT_FIELDS_CHOICES = zip(OBJECT_FIELDS, OBJECT_FIELDS)
OBJECT_FIELDS_CHOICES = zip(DISPLAY_FIELDS, DISPLAY_FIELDS)
OBJECT_FIELDS_CHOICES_WITH_TYPE = (
    ('name', 'string'),
    ('comment', 'string'),
    ('lab_id', 'string'),
    ('user_id', 'integer'),
    ('created', 'string'),
    ('creator', 'integer'),
    ('modified', 'string'),
    ('source', 'string'),
    ('organism', 'integer'),
    ('id', 'integer'),
)
PAGINATE_BY = (5, 10, 20, 30, 50, 70, 100)
PAGINATE_BY_CHOICES = zip(PAGINATE_BY, PAGINATE_BY)

class ObjectFields(forms.MultipleChoiceField):
    def valid_value(self, value):
        return True

class AllObjectFields(forms.ChoiceField):
    def valid_value(self, value):
        return True

class ObjectAttributesWidget(forms.SelectMultiple):
    def render_options(self, choices, selected_choices):
        # Rewrite standart widget.
        selected_choices = set(force_text(v) for v in selected_choices)
        output = []
        # I get choices with 3 items. This way for using standart form field
        for choice in self.choices:
            option_value, option_label = choice[:2]
            output.append(self.render_option(selected_choices, option_value, option_label))
        return '\n'.join(output)

class ObjectSortWidget(forms.Select):
    def render_options(self, choices, selected_choices):
        # Rewrite standart widget.
        selected_choices = set(force_text(v) for v in selected_choices)
        output = []
        # I get choices with 3 items. This way for using standart form field
        for choice in self.choices:
            option_value, option_label = choice[:2]
            output.append(self.render_option(selected_choices, option_value, option_label))
        return '\n'.join(output)

class SelectObjects(forms.Form):
    # request = forms.CharField(widget=forms.Textarea, required=False)
    # method = forms.ChoiceField(choices = GET_METHOD_CHOISES, initial = 'get_objects')
    organism = forms.ChoiceField(widget=forms.Select(attrs={'style': 'width:220px'}))
    display_fields = ObjectFields(required=False, 
        widget=forms.CheckboxSelectMultiple(), choices=OBJECT_FIELDS_CHOICES, initial=('name',))
    attributes_list = ObjectFields(required=False, 
        widget=ObjectAttributesWidget(attrs={'style': 'width:740px'}))
    sort_by = AllObjectFields(required=False, 
        widget=ObjectSortWidget(attrs={'style': 'width:300px'}))
    paginate_by = forms.ChoiceField(required=False, 
        widget=forms.Select(attrs={'style': 'width:80px'}), choices=PAGINATE_BY_CHOICES, initial=10)
    tags = forms.ChoiceField(required=False, 
        widget=forms.Select(attrs={'style': 'width:200px'}))
    # row_query = forms.CharField(required=False)
    # limit = forms.IntegerField(required=False)
    # skip = forms.IntegerField(required=False)

    def __init__(self, request, with_choices=True, organism_id=None, *args, **kwargs):
        super(SelectObjects, self).__init__(*args, **kwargs)
        self.request = request
        if with_choices:
            # choices_list = [('', '')]
            organism_choices_list = get_choices(request, item_name='organisms')
            self.fields['organism'].choices = organism_choices_list
            # attr_choices = self.fields['attributes_list'].choices
            if kwargs.has_key('data'):
                organism_id = kwargs['data']['organism']
            else:
                organism_id = organism_choices_list[0][0]

            if organism_id:
                query_params = {
                    "query": "organism = {}".format(organism_id),
                    "orderby" : [["name", "asc"]]
                }
                self.fields['attributes_list'].choices = get_choices(self.request, 
                    cache_key='attributes_{}'.format(organism_id), item_name='attributes', 
                    key='name', query_params = query_params, append_field='atype')
                attr_choices = self.fields['attributes_list'].choices
                # Copy list
                all_fields = list(OBJECT_FIELDS_CHOICES)
                all_fields.extend(attr_choices)
                self.fields['sort_by'].choices = all_fields

                self.fields['tags'].choices = [('','')]
                query_params = {
                    "orderby" : [["weight", "asc"]]
                }
                self.fields['tags'].choices.extend(get_choices(self.request, item_name='tags', 
                    key='tag', query_params=query_params))
                # print 333, self.fields['sort_by'].choices
            # else:
            #     self.fields['attributes_list'].choices = get_choices(request, item_name='attributes', key='name')
            

    # def clean(self):
    #     if self.cleaned_data.has_key('organism') and self.cleaned_data['organism']:
    #         organism_id = self.cleaned_data['organism']
    #         attr_field = self.fields['attributes_list']
    #         # Add choices for attributes after cleaning
    #         attr_list = get_choices(self.request, cache_key='attributes_{}'.format(organism_id), item_name='attributes', 
    #             key='name', query="organism = {}".format(organism_id), append_field='atype')
    #         attr_field.choices = attr_list
    #     return self.cleaned_data


class CreateOrganismForm(forms.Form):
    name = forms.CharField(label='Name')


# def create_object_form(request, *args, **kwargs):
class CreateObjectForm(forms.Form):
    organism = forms.ChoiceField(widget=forms.Select(attrs={'style': 'width:220px'}))
    name = forms.CharField(label='Name')
    lab_id = forms.CharField(label='laboratory ID', required=False)
    # tags = forms.CharField(required=False)
    source = forms.CharField(required=False)
    comment = forms.CharField(required=False)
    files_dict = forms.CharField(widget=forms.HiddenInput,required=False)

    def __init__(self, *args, **kwargs):
        # self.tag_method = 'object'
        # self.request = request

        super(CreateObjectForm, self).__init__(*args, **kwargs)
        self.fields['organism'].choices = get_choices(self.request, item_name='organisms')
        
        # self.fields['tags'].choices = get_choices(request, item_name='tags')


class UpdateObjectForm(CreateObjectForm, TagMixin):
    id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    version = forms.IntegerField(widget=forms.HiddenInput, required=False)
    # sequences = forms.ComboField(fields=[forms.CharField(max_length=20), forms.EmailField()])

    def __init__(self, request, *args, **kwargs):
        self.request = request
        self.tag_method = 'object'
        # TagMixin.__init__(self, request, *args, **kwargs)
        # CreateObjectForm.__init__(self, request, *args, **kwargs)
        super(UpdateObjectForm, self).__init__(*args, **kwargs)
