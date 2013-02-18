from dajax.core import Dajax
from django.utils import simplejson
from dajaxice.decorators import dajaxice_register

from django.contrib.auth.decorators import login_required

from apps.bioface.utils import ajax_login_required

@dajaxice_register
def assign_test(request):
    dajax = Dajax()
    dajax.assign('#box', 'innerHTML', 'Hello World!')
    dajax.add_css_class('div .alert', 'red')
    return dajax.json()

@dajaxice_register
def multiply(request, a, b):
    dajax = Dajax()
    result = int(a) * int(b)
    dajax.assign('#result','value',str(result))
    return dajax.json()

@dajaxice_register
def sayhello(request):
    return simplejson.dumps({'message':'Hello World'})


from dajaxice.utils import deserialize_form
from forms import ExampleForm

@dajaxice_register
def send_form(request, form):
    dajax = Dajax()
    form = ExampleForm(deserialize_form(form))

    if form.is_valid():
        dajax.remove_css_class('#my_form input', 'error')
        dajax.alert("Form is_valid(), your username is: %s" % form.cleaned_data.get('username'))
    else:
        dajax.add_css_class('#my_form input', 'error')
        for error in form.errors:
            dajax.add_css_class('#id_%s' % error, 'error')

    return dajax.json()


# from dajaxwebsite.examples.views import get_pagination_page
from django.template.loader import render_to_string
# from dajaxice.decorators import dajaxice_register

# from django.core.paginator import Paginator, InvalidPage, EmptyPage

# def get_pagination_page(page=1):
#     items = range(0, 100)
#     paginator = Paginator(items, 10)
#     try:
#         page = int(page)
#     except ValueError:
#         page = 1

#     try:
#         items = paginator.page(page)
#     except (EmptyPage, InvalidPage):
#         items = paginator.page(paginator.num_pages)

#     return items

from apps.bioface.views import get_pagination_page

@dajaxice_register
# @ajax_login_required
def pagination(request, page, method, query):
	query_dict = {
	    "method" : method,
	    "key": request.user.sessionkey,
	    # "params" : {
	    #     # "query" : "reference_id = id",
	    #     "limit" : cd['limit'],
	    #     "skip" : cd['skip'],
	    #     # "orderby" : [["field_name", "acs"], ["field_name2", "desc"]]
	    # }
	}

	template_name, template_context = get_pagination_page(page, query_dict)
	render = render_to_string('result_list_paginated.html', template_context)

	dajax = Dajax()
	dajax.assign('#result-list', 'innerHTML', render)
	return dajax.json()

@dajaxice_register
def test_span(request):
    dajax = Dajax()
    dajax.assign('#test-span', 'innerHTML', 'Hello World!')
    return dajax.json()

