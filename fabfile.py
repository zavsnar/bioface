# -*- coding: utf-8 -*-
from __future__ import with_statement

from fabric.api import *
from fabric.contrib.console import confirm

from settings import PROJECT_ROOT, SOURCE_ROOT, PROJECT_NAME

env.hosts = ['zavsnar@10.0.1.208']


def deploy():
    # local('git push')
    # code_dir = PROJECT_ROOT
    with settings(sudo_user='zavsnar'):
        sudo('ln -sf {0}supervisor.conf /etc/supervisor/conf.d/{1}.conf'.format(PROJECT_ROOT, PROJECT_NAME))
        sudo('supervisorctl update')
        sudo('ln -sf {0}nginx.conf /etc/nginx/conf.d/{1}.conf'.format(PROJECT_ROOT, PROJECT_NAME))
        sudo('service nginx restart')
        # run('git pull')
        #run('./manage.py compress')

    # run('touch /tmp/project.txt')

def configure():
    with file('{0}deploy/supervisor.template'.format(SOURCE_ROOT), 'r') as supervisor_conf:
        local_conf = supervisor_conf.read().format(project_root = PROJECT_ROOT)
    with file('{0}supervisor.conf'.format(PROJECT_ROOT), 'w') as local_supervisor:
        local_supervisor.write(local_conf)

    with file('{0}deploy/uwsgi.template'.format(SOURCE_ROOT), 'r') as uwsgi_conf:
        local_conf = uwsgi_conf.read().format(project_root = PROJECT_ROOT)
    with file('{0}uwsgi.ini'.format(PROJECT_ROOT), 'w') as local_uwsgi:
        local_uwsgi.write(local_conf)

    with file('{0}deploy/nginx.template'.format(SOURCE_ROOT), 'r') as nginx_conf:
        local_conf = nginx_conf.read() % {'project_root': PROJECT_ROOT}
    with file('{0}nginx.conf'.format(PROJECT_ROOT), 'w') as local_nginx:
        local_nginx.write(local_conf)

def celery():
    run('supervisorctl restart bioface')


def status():
    run('supervisorctl status')