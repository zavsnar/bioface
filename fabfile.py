# -*- coding: utf-8 -*-
from __future__ import with_statement

from fabric.api import *
from fabric.contrib.console import confirm

from settings import PROJECT_ROOT, SOURCE_ROOT

# env.hosts = ['root@host']


def deploy():
    # local('git push')
    # code_dir = PROJECT_ROOT
    with cd(SOURCE_ROOT):
        run('sudo ln -s {root}deploy/nginx.conf /etc/nginx/conf.d/bioface.conf'.format(PROJECT_ROOT))
        run('service nginx restart')
        run('sudo ln -s {root}deploy/supervisor.conf /etc/supervisor/conf.d/bioface.conf'.format(PROJECT_ROOT))
        run('supervisorctl update')
        # run('git pull')
        #run('./manage.py compress')

    # run('touch /tmp/project.txt')


def celery():
    run('supervisorctl restart bioface')


def status():
    run('supervisorctl status')


def uptime():
    run('uptime')