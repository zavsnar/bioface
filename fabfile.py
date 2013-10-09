# -*- coding: utf-8 -*-
from __future__ import with_statement

from fabric.api import *

from local_settings import SOURCE_ROOT, PROJECT_NAME, HOST_NAME, UWSGI_PORT

env.hosts = ['zavsnar@10.0.1.208']

PROJECT_ROOT = SOURCE_ROOT + '../'

# Generate config files from templates
def configure():
    with file('{0}deploy/supervisor.template'.format(SOURCE_ROOT), 'r') as supervisor_conf:
        local_conf = supervisor_conf.read().format(project_root = PROJECT_ROOT, source_root = SOURCE_ROOT, project_name = PROJECT_NAME)
    with file('{0}supervisor.conf'.format(PROJECT_ROOT), 'w') as local_supervisor:
        local_supervisor.write(local_conf)

    with file('{0}deploy/uwsgi.template'.format(SOURCE_ROOT), 'r') as uwsgi_conf:
        local_conf = uwsgi_conf.read().format(project_root = PROJECT_ROOT, project_name = PROJECT_NAME, uwsgi_port = UWSGI_PORT)
    with file('{0}uwsgi.ini'.format(PROJECT_ROOT), 'w') as local_uwsgi:
        local_uwsgi.write(local_conf)

    with file('{0}deploy/nginx.template'.format(SOURCE_ROOT), 'r') as nginx_conf:
        local_conf = nginx_conf.read() % {'project_root': PROJECT_ROOT, 'host_name': HOST_NAME, 'uwsgi_port': UWSGI_PORT}
    with file('{0}nginx.conf'.format(PROJECT_ROOT), 'w') as local_nginx:
        local_nginx.write(local_conf)

def celery():
    run('supervisorctl restart {0}'.format(PROJECT_NAME))


def status():
    run('supervisorctl status')