#!/bin/bash

echo "AppendLibraryPath: $(pwd)" > .a2psrc

for file in *.txt; do
	a2ps --font-size=9 -o "${file}.ps" --columns=4 -Mletter "$file" -B --right-footer="${file} %s./%s#" --prologue=smi
    # a2ps -o "${file}.ps" -R -Mletter "$file"
    ps2pdf "${file}.ps"
done
