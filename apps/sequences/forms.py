from __future__ import unicode_literals
from __future__ import absolute_import

from django import forms
from django.core.cache import cache
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from apps.common.utils import api_request, get_choices

class CreateSequenceForm(forms.Form):
    name = forms.CharField(label='Name')
    ploid = forms.IntegerField()
    index = forms.IntegerField(help_text="Number sequence in file")
    length = forms.IntegerField()

    object_id = forms.ChoiceField(widget=forms.Select(attrs={'style': 'width:220px'}))
    source = forms.CharField(required=False)
    comment = forms.CharField(required=False)
    file = forms.CharField()
    regions = forms.IntegerField()

    def __init__(self, request, *args, **kwargs):
        super(CreateSequenceForm, self).__init__(*args, **kwargs)
        self.request = request
        self.fields['object_id'].choices = get_choices(request, cache_key='objects')
