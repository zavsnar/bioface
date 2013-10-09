from __future__ import unicode_literals
# from __future__ import print_function
from __future__ import absolute_import

from django import forms
from django.core.cache import cache
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

#from django_select2 import *
#from django_select2.widgets import *

from apps.common.utils import api_request, get_choices

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

class CreateSequenceForm(forms.Form):
    name = forms.CharField(label='Name')
    ploid = forms.IntegerField()
    index = forms.IntegerField(help_text="Number sequence in file")
    length = forms.IntegerField()

    object_id = forms.ChoiceField(widget=forms.Select(attrs={'style': 'width:220px'}))
    # tags = forms.CharField(required=False)
    source = forms.CharField(required=False)
    comment = forms.CharField(required=False)
    file = forms.CharField()
    regions = forms.IntegerField()

    def __init__(self, request, *args, **kwargs):
        super(CreateSequenceForm, self).__init__(*args, **kwargs)
        self.request = request
        self.fields['object_id'].choices = get_choices(request, cache_key='objects')
