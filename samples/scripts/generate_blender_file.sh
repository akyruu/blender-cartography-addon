#!/bin/bash

if [ $# -eq 0 ]; then
  echo "A parameter is required: file"
  exit 1
fi

action="generate_blender_file";
file=$1;
output=${file/%.tsv/.blend};
output=${output/%.csv/.blend};
output=${output/files/generated};

echo "Launch python script in blender"
echo "Parameters: action=$action, file=$file, output=$output"
blender --background --python samples/blender-cartography-addon-exec.py --\
  -a $action -f $file -o $output