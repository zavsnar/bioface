#!/bin/bash

cd `dirname "$0"`;
DATABASE_PATH="../../database";
PYTHON_PATH="../../env/bin/python";
MANAGE_PATH="../manage.py";

rm $DATABASE_PATH;
$PYTHON_PATH $MANAGE_PATH syncdb --noinput;
$PYTHON_PATH $MANAGE_PATH loaddata users;
# $PYTHON_PATH $MANAGE_PATH loaddata tasks_bids.yaml courier-delivery_comments financial_accounts;