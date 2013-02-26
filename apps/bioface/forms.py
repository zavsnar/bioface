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

ATYPE_ATTRIBUTES = ("integer", "string", "float", "scale", "nominal", "range")
ATYPE_ATTRIBUTES_CHOISES = zip(ATYPE_ATTRIBUTES, ATYPE_ATTRIBUTES)
ATTRIBUTES_STATE = ((1, 'Primary attribute'),(0, 'Secondary attribute'))


class GetRequestAPIForm(forms.Form):
    # request = forms.CharField(widget=forms.Textarea, required=False)
    method = forms.ChoiceField(choices = GET_METHOD_CHOISES)
    # row_query = forms.CharField(required=False)
    # limit = forms.IntegerField(required=False)
    # skip = forms.IntegerField(required=False)


class RegistrationForm(UserCreationForm):
    username = forms.EmailField(label="E-mail", max_length=70)

def get_choices(request, cache_key):
	# if cache.has_key(cache_key):
	# 	choices_list = cache.get(cache_key)
	# else:
	if cache_key:
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
				choices_list.append((int(item['id']), title))
			# choices_list = [ (item['id'], item['name']) for item in item_list ]
			cache.set(cache_key, choices_list, 30)

		# print choices_list
	return choices_list

class QueryMethodForm(forms.Form):
		method = forms.MultipleChoiceField(label='Add', choices=CREATE_METHOD_CHOISES, 
	    	required=False, widget=forms.SelectMultiple(attrs={'style': 'width:220px', 'class': 'select_method'}))

class CreateOrganismForm(forms.Form):
	name = forms.CharField(label='Name')

# def create_object_form(request, *args, **kwargs):
class CreateObjectForm(forms.Form):
	name = forms.CharField(label='Name')
	lab_id = forms.CharField(label='laboratory ID', required=False)
	organism = forms.ChoiceField(widget=forms.Select(attrs={'style': 'width:220px'}))
	source = forms.CharField(required=False)
	comment = forms.CharField(required=False)

	def __init__(self, request, *args, **kwargs):
		super(CreateObjectForm, self).__init__(*args, **kwargs)
		self.fields['organism'].choices = get_choices(request, cache_key='organisms')
		
			
	# return CreateObjectForm(*args, **kwargs)


class UpdateObjectForm(CreateObjectForm):
	id = forms.IntegerField(widget=forms.HiddenInput, required=False)
	version = forms.IntegerField(widget=forms.HiddenInput, required=False)
	# sequences = forms.ComboField(fields=[forms.CharField(max_length=20), forms.EmailField()])


class MultipleInputWidget(forms.widgets.MultipleHiddenInput):
	input_type = 'text'
	is_hidden = False

class CustomMultipleField(forms.MultipleChoiceField):
    widget = MultipleInputWidget

    def validate(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages['required'])

class CreateAttributeForm(forms.Form):
	name = forms.CharField(label='Name')
	atype = forms.ChoiceField(choices=ATYPE_ATTRIBUTES_CHOISES)
	organism = forms.ChoiceField(widget=forms.Select(attrs={'style': 'width:220px'}))
	primary = forms.ChoiceField(widget=forms.RadioSelect, choices=ATTRIBUTES_STATE, initial=1)
	
	descr_integer_default = forms.IntegerField()
	descr_string_default = forms.CharField()
	descr_float_default = forms.FloatField()

	descr_range_default = forms.FloatField()
	descr_range_from = forms.FloatField()
	descr_range_to = forms.FloatField()

	descr_nominal = CustomMultipleField()
	descr_nominal_default = forms.CharField()
	
	descr_scale = forms.CharField()
	descr_scale_default = forms.CharField()

	# def clean_descr_nominal(self):
	# 	print 88888, self.fields['descr_nominal']
	# 	self.fields['descr_nominal']._set_choices()
	

	# descr = forms.CharField(label="Description", widget=forms.Textarea)

	def __init__(self, request, *args, **kwargs):
		super(CreateAttributeForm, self).__init__(*args, **kwargs)
		self.fields['organism'].choices = get_choices(request, cache_key='organisms')


	#TODO Validation for string-fields
	def clean(self):
		cd = super(CreateAttributeForm, self).clean()
		atype = cd['atype']
		description_field_list = ['descr_integer_default', 'descr_string_default', 'descr_float_default',
			'descr_range_default', 'descr_range_from', 'descr_range_to',
			'descr_nominal', 'descr_nominal_default', 'descr_scale', 'descr_scale_default']
		print 88888, self.fields['descr_nominal']
		if atype == 'integer':
			description_field_list.remove('descr_integer_default')
		elif atype == 'string':
			description_field_list.remove('descr_string_default')
		elif atype == 'float':
			description_field_list.remove('descr_float_default')
		elif atype == 'range':
			description_field_list.remove('descr_range_default')
			description_field_list.remove('descr_range_from')
			description_field_list.remove('descr_range_to')
		elif atype == 'nominal':
			description_field_list.remove('descr_nominal')
			description_field_list.remove('descr_nominal_default')
		elif atype == 'scale':
			description_field_list.remove('descr_scale')
			description_field_list.remove('descr_scale_default')

		for field in description_field_list:
			if self._errors.has_key(field):
				del self._errors[field]
		return cd


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
