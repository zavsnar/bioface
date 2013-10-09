
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from apps.common.utils import LoginFailError

class LoginRedirectMiddleware(object):
    def process_exception(self, request, e):
        if isinstance(e, LoginFailError):
            return HttpResponseRedirect(reverse('signin'))
        return None