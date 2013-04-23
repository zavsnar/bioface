from __future__ import unicode_literals
# from __future__ import print_function
from __future__ import absolute_import

from django import forms
from django.core.cache import cache
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib import messages

#from django_select2 import *
#from django_select2.widgets import *

from apps.bioface.utils import api_request, get_choices
from apps.bioface.models import Download

METHODS_FOR_CALL_ITEM = ("get_object", "get_attribute", "get_tag", "get_tags_version", "get_sequence", "get_reference",
    "get_segment", "get_alignment", "get_annotation")
METHODS_FOR_CALL_ITEMS = ("get_attributes", "get_tags", "get_sequences", "get_references", 
    "get_segments", "get_alignments", "get_annotations", "get_objects")

METHODS_FOR_CREATE_ITEM = ("add_segment", "add_object")

CREATE_METHOD_CHOISES = [ (i, i.replace('add_', '')) for i in METHODS_FOR_CREATE_ITEM ]

GET_METHOD_CHOISES = zip(METHODS_FOR_CALL_ITEMS, METHODS_FOR_CALL_ITEMS)
# METHOD_CHOISES.append(("get_objects", "get_objects"))

ATYPE_ATTRIBUTES = ("integer", "string", "float", "scale", "nominal", "range")
ATYPE_ATTRIBUTES_CHOISES = zip(ATYPE_ATTRIBUTES, ATYPE_ATTRIBUTES)
ATTRIBUTES_STATE = ((1, 'Primary attribute'),(0, 'Secondary attribute'))

OBJECT_DOWNLOAD_OPTIONS = (
    ('attributes', 'attributes'),
    ('sequences', 'sequences'),
)

# class ExampleForm(forms.Form):
#     # request = forms.CharField(widget=forms.Textarea, required=False)
#     method = forms.ChoiceField(choices = GET_METHOD_CHOISES)
#     # row_query = forms.CharField(required=False)
#     # limit = forms.IntegerField(required=False)
#     # skip = forms.IntegerField(required=False)

class DownloadForm(forms.ModelForm):
    description = forms.CharField(required=True, max_length=255, 
        widget=forms.Textarea(attrs={'rows':2, 'style':'width: 400px;'}))
    # encodding = forms.CharField(max_length=100, required=False)
    options = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple(), 
        choices=OBJECT_DOWNLOAD_OPTIONS)

    class Meta:
    	model = Download
    	fields = ('description', 'encoding')

class GetRequestAPIForm(forms.Form):
    # request = forms.CharField(widget=forms.Textarea, required=False)
    method = forms.ChoiceField(choices = GET_METHOD_CHOISES)
    # row_query = forms.CharField(required=False)
    # limit = forms.IntegerField(required=False)
    # skip = forms.IntegerField(required=False)

class RegistrationForm(UserCreationForm):
    username = forms.EmailField(label="E-mail", max_length=70)

# def get_choices(request, cache_key, key='id'):
# 	# if cache.has_key(cache_key):
# 	# 	choices_list = cache.get(cache_key)
# 	# else:
# 	if cache_key:
# 		method = 'get_{}'.format(cache_key)
# 		query_dict = {
#             "method" : method,
#             "key": request.user.sessionkey,
#         }

# 		content_dict = api_request(query_dict)

# 		item_list = content_dict['result'].get(cache_key, [])
# 		choices_list=[('','')]
# 		if item_list:
# 			for item in item_list:
# 				if item.has_key('name'):
# 					title = item['name']
# 				elif item.has_key('tag'):
# 					title = item['tag']
# 				choices_list.append((item[key], title))
# 			# cache.set(cache_key, choices_list, 30)

# 		# print choices_list
# 	return choices_list

# "params" : {
#     "query" : "field > 12 and (field2 = green and field64 > big)",
#     "limit" : int,
#     "skip": int,
#     "orderby" : [["field_name", "asc"], ["field_name2", "desc"]]
#     "attributes_list": ["attribute_name1", "attribute_name2",  ]
# }
# class SelectObjects(forms.Form):
#     # request = forms.CharField(widget=forms.Textarea, required=False)
#     method = forms.ChoiceField(choices = GET_METHOD_CHOISES, initial = 'get_objects')
#     attributes_list = forms.MultipleChoiceField(required=False, widget=forms.SelectMultiple(attrs={'style': 'width:220px'}))
#     # row_query = forms.CharField(required=False)
#     # limit = forms.IntegerField(required=False)
#     # skip = forms.IntegerField(required=False)

#     def __init__(self, request, *args, **kwargs):
# 		super(SelectObjects, self).__init__(*args, **kwargs)
# 		self.fields['attributes_list'].choices = get_choices(request, cache_key='attributes', key='name')

class QueryMethodForm(forms.Form):
		method = forms.MultipleChoiceField(label='Add', choices=CREATE_METHOD_CHOISES, 
	    	required=False, widget=forms.SelectMultiple(attrs={'style': 'width:220px', 'class': 'select_method'}))

class CreateOrganismForm(forms.Form):
	name = forms.CharField(label='Name')

class TagMixin(forms.Form):
    old_tags = forms.CharField(widget=forms.HiddenInput, required=False)
    tags = forms.CharField(label = 'Tags', required=False, 
        widget=forms.TextInput(attrs={'style': 'width:220px'}))

    def __init__(self, *args, **kwargs):
        super(TagMixin, self).__init__(*args, **kwargs)
        # self.request = request
        # self.fields['tags'].choices = [('','')]
        self.fields['tags'].choices = get_choices(self.request, item_name='tags', key="tag")
        # self.fields['old_tags'] = self.fields['tags']

    def clean(self):
        if self.cleaned_data['tags'] != self.cleaned_data['old_tags']:
            new_tags = self.cleaned_data['tags'].split(',')
            old_tags = self.cleaned_data['old_tags'].split(',')
            add_tags = list(set(new_tags) - set(old_tags))

            if add_tags:
                query_add_tag = {
                    "method": "tag_{}".format(self.tag_method),
                    "key": self.request.user.sessionkey,
                    "params": {
                          "id": self.cleaned_data['id'],
                          "tags": add_tags
                    }
                }

                content_dict = api_request(query_add_tag)
                if content_dict.has_key('error'):
                    messages.error(self.request, 'ERROR: {}'.format(content_dict['error']))

            delete_tags = list(set(old_tags) - set(new_tags))
            if delete_tags:
                query_delete_tag = {
                    "method": "untag_{}".format(self.tag_method),
                    "key": self.request.user.sessionkey,
                    "params": {
                        "id": self.cleaned_data['id'],
                        "tags": delete_tags
                    }
                }

                content_dict = api_request(query_delete_tag)
                if content_dict.has_key('error'):
                    messages.error(self.request, 'ERROR: {}'.format(content_dict['error']))

            if (add_tags or delete_tags) and cache.get('tags', None):
                cache.delete('tags')

        return self.cleaned_data


class MultipleInputWidget(forms.widgets.MultipleHiddenInput):
	input_type = 'text'
	is_hidden = False

class CustomMultipleField(forms.MultipleChoiceField):
    widget = MultipleInputWidget

    def validate(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages['required'])


class InlineSequenseForm(forms.Form):
	name = forms.CharField(label='Name')
	ploid = forms.IntegerField()
	index = forms.IntegerField()
	organism = forms.CharField()

class CreateUpdateSequense(InlineSequenseForm):
	tags = forms.ComboField(fields=[forms.CharField(max_length=20), forms.EmailField()])

def add_update_segment_form(request, *args, **kwargs):
	class AddUpdateSegmentForm(forms.Form):
		# "name": "str",
	 #    "ploid": int,
	 #    "sequence" : sequence_id,
	 #    "comment": "str",
	 #    "struct": "str",
	 #    "annotations": ["id", "id2"],
	 #    "tags": ["id", "id"],
	 #    "reference": reference_id

	    name = forms.CharField(label='Name')
	    ploid = forms.IntegerField(label='Ploidy', required=False)
	    sequence = forms.ChoiceField(choices=get_choices(request, cache_key='sequences'), 
	    	widget=forms.Select(attrs={'style': 'width:220px'}))
	    comment = forms.CharField(label='Comment', required=False)
	    struct = forms.CharField(label='Structure', required=False)
	    annotations = forms.MultipleChoiceField(choices=get_choices(request, cache_key='annotations'), 
	    	required=False, widget=forms.SelectMultiple(attrs={'style': 'width:220px'}))
	    tags = forms.MultipleChoiceField(choices=get_choices(request, cache_key='tags'), 
	    	required=False, widget=forms.SelectMultiple(attrs={'style': 'width:220px'}))
	    reference = forms.ChoiceField(choices=get_choices(request, cache_key='references'), 
	    	required=False, widget=forms.Select(attrs={'style': 'width:220px'}))

	return AddUpdateSegmentForm(*args, **kwargs)
