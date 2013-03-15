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

class ExampleForm(forms.Form):
    username = forms.CharField(max_length=30, label=u'Username')
    email = forms.EmailField(label=u'Email address')

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

# "params" : {
#     "query" : "field > 12 and (field2 = green and field64 > big)",
#     "limit" : int,
#     "skip": int,
#     "orderby" : [["field_name", "asc"], ["field_name2", "desc"]]
#     "attributes_list": ["attribute_name1", "attribute_name2",  ]
# }
class SelectObjects(forms.Form):
    # request = forms.CharField(widget=forms.Textarea, required=False)
    method = forms.ChoiceField(choices = GET_METHOD_CHOISES, initial = 'get_objects')
    attributes_list = forms.MultipleChoiceField(required=False, widget=forms.SelectMultiple(attrs={'style': 'width:220px'}))
    # row_query = forms.CharField(required=False)
    # limit = forms.IntegerField(required=False)
    # skip = forms.IntegerField(required=False)

    def __init__(self, request, *args, **kwargs):
		super(SelectObjects, self).__init__(*args, **kwargs)
		self.fields['attributes_list'].choices = get_choices(request, cache_key='attributes', key='name')

class CreateSequenceForm(forms.Form):
	name = forms.CharField(label='Name')
	object_id = forms.ChoiceField(widget=forms.Select(attrs={'style': 'width:220px'}))
	tags = forms.CharField(required=False)
	source = forms.CharField(required=False)
	comment = forms.CharField(required=False)

	def __init__(self, request, *args, **kwargs):
		super(CreateObjectForm, self).__init__(*args, **kwargs)
		self.request = request
		self.fields['object_id'].choices = get_choices(request, cache_key='object')

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
					"params": {
					    "data": {
					        "tag": tag
				        }
				    }
				}

				content_dict = api_request(query_dict)
				print 5555, content_dict
				if content_dict['result']:
					new_tags.append(content_dict['result']['id'])

		tags.extend(new_tags)

		if new_tags:
			self.fields['tags'].choices = get_choices(self.request, cache_key='tags')

		self.cleaned_data['tags'] = tags
		print 7777, self.cleaned_data['tags']
		return self.cleaned_data['tags']
	# return CreateObjectForm(*args, **kwargs)
