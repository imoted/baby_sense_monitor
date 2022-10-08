#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

python3 $SCRIPT_DIR/upload_data.py &
python3 $SCRIPT_DIR/rest_api.py &
$SCRIPT_DIR/lepton/build/lepton
