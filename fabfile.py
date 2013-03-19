# -*- coding: utf-8 -*-
from __future__ import with_statement

from fabric.api import *
from fabric.contrib.console import confirm

from settings import PROJECT_ROOT, SOURCE_ROOT

env.hosts = ['zavsnar@10.0.1.36']


def deploy():
    # local('git push')
    # code_dir = PROJECT_ROOT
    with cd(SOURCE_ROOT):
	with settings(sudo_user='zavsnar'):
            sudo('ln -sf {0}/deploy/nginx.conf /etc/nginx/conf.d/bioface.conf'.format(SOURCE_ROOT))
            sudo('service nginx restart')
            sudo('ln -sf {0}/deploy/supervisor.conf /etc/supervisor/conf.d/bioface.conf'.format(SOURCE_ROOT))
            sudo('supervisorctl update')
        # run('git pull')
        #run('./manage.py compress')

    # run('touch /tmp/project.txt')


def celery():
    run('supervisorctl restart bioface')


def status():
    run('supervisorctl status')


def uptime():
    run('uptime')
