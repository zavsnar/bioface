from __future__ import unicode_literals
# from __future__ import print_function
from __future__ import absolute_import

from django import forms
from django.core.cache import cache
from django.contrib.auth.forms import UserCreationForm

from apps.bioface.utils import api_request

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

class GetRequestAPIForm(forms.Form):
    request = forms.CharField(widget=forms.Textarea, required=False)
    method = forms.ChoiceField(choices = GET_METHOD_CHOISES)
    row_query = forms.CharField(required=False)
    limit = forms.IntegerField(required=False)
    skip = forms.IntegerField(required=False)


class RegistrationForm(UserCreationForm):
    username = forms.EmailField(label="E-mail", max_length=70)

def get_choices(request, cache_key):
	if cache.has_key(cache_key):
		choices_list = cache.get(cache_key)
	else:
		method = 'get_{}'.format(cache_key)
		query_dict = {
            "method" : method,
            "key": request.user.sessionkey,
        }

		http_response, content_dict = api_request(query_dict)

		item_list = content_dict['result'].get(cache_key, [])
		choices_list=[('','')]
		if item_list:
			for item in item_list:
				if item.has_key('name'):
					title = item['name']
				elif item.has_key('tag'):
					title = item['tag']
				choices_list.append((item['id'], title))
			# choices_list = [ (item['id'], item['name']) for item in item_list ]
			cache.set(cache_key, choices_list, 30)

		# print choices_list
	return choices_list

class QueryMethodForm(forms.Form):
		method = forms.MultipleChoiceField(label='Add', choices=CREATE_METHOD_CHOISES, 
	    	required=False, widget=forms.SelectMultiple(attrs={'style': 'width:220px', 'class': 'select_method'}))

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
