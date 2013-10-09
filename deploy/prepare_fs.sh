#!/bin/bash

# Prepare filesystem (mkdir)

cd `dirname "$0"`;
BRANCH_ROOT="../../"
USER_NAME=$USER

make_dirs(){
    (
        cd $BRANCH_ROOT
        echo -n "Creating folders..."
        mkdir -p \
                static \
                media \
                media/downloads \
                logs \
            && echo "  ok" \
            || echo "  ERROR!" 1>&2;
    )
}

if [ "$1" ]; then
    make_dirs;
    # echo "Creating virtual python environment..."
    # ./env_update.sh "$1" \
    #     && echo "  ok" \
    #     || echo "  ERROR!" 1>&2;
    cd "$BRANCH_ROOT";
    REALPATH=$(readlink -f local_settings.py)
    if [ ! -e $REALPATH ]; then
        echo "from default_local_settings import *" > local_settings.py
    fi;
else
   echo "Error: python version requires as first argument" 1>&2;
fi