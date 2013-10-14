from celery import task
import zipfile
import zlib
import tempfile
import codecs

from csv_unicode_recoder import UnicodeWriter

from settings import DOWNLOADS_ROOT
from apps.common.utils import api_request

# load objects from query
@task()
def loading_objects(object_download_id, query_dict, with_attributes=False, with_sequences=False, encoding='utf-8'):
    content_dict = api_request(query_dict)
    if content_dict.has_key('result'):
        objects = content_dict['result']['objects']
        with tempfile.NamedTemporaryFile(delete=False) as obj_csvfile:
            spamwriter = UnicodeWriter(obj_csvfile, encoding=encoding, quoting=csv.QUOTE_NONE, delimiter = ';')

            col_list = []
            attr_col_list = []
            for key, val in objects[0].iteritems():
                if key == 'attributes':
                    attr_col_list = [ attr['name'] for attr in val ]
                else:
                    col_list.append(key)
            col_list.extend(attr_col_list)

            spamwriter.writerow(col_list)
            for obj in objects:
                obj_vals = []
                obj_attrs_val = [ None for i in attr_col_list ]
                for key, val in obj.iteritems():
                    if key == 'attributes':
                        for attr in val:
                            idx = attr_col_list.index(attr['name'])
                            attr_value = attr['value']
                            obj_attrs_val[idx] = attr_value
                    else:
                        obj_vals.append(val)

                obj_vals.extend(obj_attrs_val)
                spamwriter.writerow(obj_vals)

        csv_files_list = [('objects.csv', obj_csvfile.name)]

        if with_attributes:
            # Get all attributes from select objects
            if query_dict['params'].has_key('attributes_list'):
                del query_dict['params']['attributes_list']

            content_dict = api_request(query_dict)
            if content_dict.has_key('result'):
                objects = content_dict['result']['objects']

                with tempfile.NamedTemporaryFile(delete=False) as attr_csvfile:
                    spamwriter = UnicodeWriter(attr_csvfile, encoding=encoding)
                    attr_col_list = ['Objects']
                    attr_col_list.extend([ attr['name'] for attr in objects[0]['attributes'] ])
                    spamwriter.writerow(attr_col_list)
                    for obj in objects:
                        obj_attrs_val = [ None for i in attr_col_list ]
                        for attr in obj['attributes']:
                            idx = attr_col_list.index(attr['name'])
                            obj_attrs_val[idx] = attr['value']
                        obj_attrs_val[0] = obj['name']

                        spamwriter.writerow(obj_attrs_val)

                csv_files_list.append(('attributes.csv', attr_csvfile.name))

        if with_sequences:
            # TODO
            pass

        zip_file_name = 'download_id_{}.zip'.format(object_download_id)
        zip_file_path = DOWNLOADS_ROOT + zip_file_name
        with zipfile.ZipFile(zip_file_path, 'w') as myzip:
            
            compression = zipfile.ZIP_DEFLATED
            for file_name, file_path in csv_files_list:
                myzip.write(file_path, arcname=file_name, compress_type=compression)
    else:
        return 'Error: {}'.format(content_dict['error']['message'])
        
    return zip_file_name