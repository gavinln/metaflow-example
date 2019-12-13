#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

start_notebook() {
    local NOTEBOOK_DIR=$SCRIPT_DIR/..
    pipenv run jupyter notebook --no-browser --notebook-dir=$BASIC_NOTEBOOKS
}

start_notebook


