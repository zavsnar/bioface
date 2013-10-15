from __future__ import unicode_literals
from __future__ import absolute_import

from django import forms
from django.core.cache import cache
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib import messages

from apps.common.utils import api_request, get_choices
from apps.common.models import Download

ATYPE_ATTRIBUTES = ("integer", "string", "float", "scale", "nominal", "range")
ATYPE_ATTRIBUTES_CHOISES = zip(ATYPE_ATTRIBUTES, ATYPE_ATTRIBUTES)
ATTRIBUTES_STATE = ((1, 'Primary attribute'),(0, 'Secondary attribute'))

OBJECT_DOWNLOAD_OPTIONS = (
    ('attributes', 'attributes'),
    ('sequences', 'sequences'),
)

class DownloadForm(forms.ModelForm):
    description = forms.CharField(required=True, max_length=255, 
        widget=forms.Textarea(attrs={'rows':2, 'style':'width: 400px;'}))
    options = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple(), 
        choices=OBJECT_DOWNLOAD_OPTIONS)

    class Meta:
    	model = Download
    	fields = ('description', 'encoding')

class RegistrationForm(UserCreationForm):
    username = forms.EmailField(label="E-mail", max_length=70)

class CreateOrganismForm(forms.Form):
	name = forms.CharField(label='Name')


class TagMixin(forms.Form):
    """
        Add tag to some form.
        Except request in self.
    """
    old_tags = forms.CharField(widget=forms.HiddenInput, required=False)
    tags = forms.CharField(label = 'Tags', required=False, 
        widget=forms.TextInput(attrs={'style': 'width:220px'}))

    def __init__(self, *args, **kwargs):
        super(TagMixin, self).__init__(*args, **kwargs)
        self.fields['tags'].choices = get_choices(self.request, item_name='tags', key="tag")

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
