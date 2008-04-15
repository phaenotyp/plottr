from django.conf import settings
from django.http import HttpResponseServerError


# Returns a simplified Error-page if there was an exception and the request 
# came via XHR 
# see http://www.djangosnippets.org/snippets/650/
class AJAXSimpleExceptionResponse:
    def process_exception(self, request, exception):
        if settings.DEBUG:
            if request.META.get('HTTP_X_REQUESTED_WITH', None) == 'XMLHttpRequest':
                import sys, traceback
                (exc_type, exc_info, tb) = sys.exc_info()
                response = "%s\n" % exc_type.__name__
                response += "%s\n\n" % exc_info
                response += "TRACEBACK:\n"    
                for tb in traceback.format_tb(tb):
                    response += "%s\n" % tb
                return HttpResponseServerError(response)

