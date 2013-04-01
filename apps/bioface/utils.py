import urllib
import httplib2 
import json
import csv, codecs, cStringIO

from django.shortcuts import render, render_to_response, redirect
from django.core.cache import cache

from settings import API_URL

# API_URL = 'http://10.0.1.7:5000/api/v1/'
# API_URL = 'https://10.0.1.208:5000/api/v1/'

def api_request(query_dict):
    
    headers = {'Content-type': 'application/json'}
    http = httplib2.Http(disable_ssl_certificate_validation=True)
    print 77777, query_dict
    http_response, content = http.request(API_URL, 'POST', body = json.dumps(query_dict), headers = headers)
    print 888, content
    try:
        content_dict = json.loads(content)
        if content_dict.has_key('error'):
            if content_dict['error']['message'] == 'invalid session':
                return redirect('signin')
    except ValueError:
        content_dict = {
            'error': {
                'message': 'Error',
                'data': 'Error'
            }
        }
        content_dict['error']['message']


    return content_dict


def ajax_login_required(view_func):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated():
            return view_func(request, *args, **kwargs)

        json = simplejson.dumps({ 'not_authenticated': True })
        return HttpResponse(json, mimetype='application/json')
    wrap.__doc__ = view_func.__doc__
    wrap.__dict__ = view_func.__dict__
    return wrap

def get_choices(request, item_name, cache_key='', key='id', query='', append_field=''):
    # choices_list = []
    
    if not cache_key:
        cache_key = item_name
    # if cache.has_key(cache_key):
        print "CACHE ", cache_key
    choices_list = cache.get(cache_key, [])
    # else:
    # choices_list = (('',''),)
    # if cache_key:

    if not choices_list:
        method = 'get_{}'.format(item_name)
        query_dict = {
            "method" : method,
            "key": request.user.sessionkey,
        }

        if query:
            query_dict['params'] = {}
            query_dict['params']['query'] = query
        # print 1111, query_dict
        content_dict = api_request(query_dict)
        

        item_list = content_dict['result'].get(item_name, [])
        # choices_list=[]
        if item_list:
            for item in item_list:
                title = item['tag'] if item.has_key('tag') else item['name']
                # if item.has_key('name'):
                #     title = item['name']
                # elif item.has_key('tag'):
                #     title = item['tag']

                if append_field:
                    # print 77777, item
                    append = item[append_field]
                    choices_list.append((item[key], title, append))
                    # choices_list.append((item[key], title))
                else:
                    choices_list.append((item[key], title))
            # print 88888, choices_list
            # raise
            cache.set(cache_key, choices_list, 3600)

        # print choices_list
    # print 1111, choices_list
    return choices_list



class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()
        self.encoding = encoding

        if encoding == 'utf-8':
            self.stream.write(codecs.BOM_UTF8)

    def writerow(self, row):
        raw_list = []
        for s in row:
            if type(s) in (str, unicode):
                raw_list.append(s.encode("utf-8"))
            else:
                raw_list.append(s)
        self.writer.writerow(raw_list)
        # self.writer.writerow([s.encode("utf-8") for s in row ])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        # data = self.encoder.encode(data)
        data = data.encode(self.encoding)
        print 3333, data.decode(self.encoding)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)