from __future__ import unicode_literals
# from __future__ import print_function
from __future__ import absolute_import

from django import forms
from django.core.cache import cache
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

#from django_select2 import *
#from django_select2.widgets import *

from apps.bioface.utils import api_request, get_choices

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
    # primary = forms.ChoiceField(widget=forms.RadioSelect, choices=ATTRIBUTES_STATE, initial=1)
    
    descr_integer_default = forms.IntegerField()
    descr_string_default = forms.CharField()
    descr_float_default = forms.FloatField()

    descr_range_default = forms.FloatField()
    descr_range_from = forms.FloatField()
    descr_range_to = forms.FloatField()

    # descr_nominal = CustomMultipleField()
    # descr_nominal_default = forms.CharField()
    
    # descr_scale = CustomMultipleField()
    # descr_scale_default = forms.CharField()

    def __init__(self, request, *args, **kwargs):
        super(CreateAttributeForm, self).__init__(*args, **kwargs)
        self.fields['organism'].choices = get_choices(request, item_name='organisms')


    #TODO Validation for string-fields
    def clean(self):
        cd = super(CreateAttributeForm, self).clean()
        atype = cd['atype']
        # All description-fields
        description_field_list = ['descr_integer_default', 'descr_string_default', 'descr_float_default',
            'descr_range_default', 'descr_range_from', 'descr_range_to']
            # 'descr_nominal', 'descr_nominal_default', 'descr_scale', 'descr_scale_default']

        # Remove selected field form description-fields
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
        # elif atype == 'nominal':
        #   description_field_list.remove('descr_nominal')
        #   description_field_list.remove('descr_nominal_default')
        # elif atype == 'scale':
        #   description_field_list.remove('descr_scale')
        #   description_field_list.remove('descr_scale_default')

        # Delete all description-fields exclude selected
        for field in description_field_list:
            if self._errors.has_key(field):
                del self._errors[field]
        return cd

class EditAttributeForm(CreateAttributeForm):
    id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    version = forms.IntegerField(widget=forms.HiddenInput, required=False)





