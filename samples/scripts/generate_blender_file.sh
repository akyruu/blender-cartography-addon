#!/bin/bash

if [ $# -eq 0 ]; then
  echo "A parameter is required: file"
  exit 1
fi

action="generate_blender_file";
file=$1;
export=${file/%.tsv/.blend};
export=${export/%.csv/.blend};
export=${export/files/generated};

echo "Launch python script in blender"
echo "Parameters: action=$action, file=$file, export=$export"
blender --background --python samples/blender-cartography-addon-exec.py --\
  -a $action -f $file -e $export