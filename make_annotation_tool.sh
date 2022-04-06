#!/bin/bash

alias my_s3cmd="s3cmd -c ~/.s3cfg-southeast-us"
for i in $(my_s3cmd ls s3://pollen-id/raw_data/ | grep s3://.*\.jpg -oh)
do
	dir=$(mktemp  -d)
	filename=$(basename $i)
	my_s3cmd get $i ${dir}/${filename}
	echo ${filename}
	ls ${dir}

	convert -crop 1024x1024 ${dir}/${filename} ${dir}/${filename%%.*}-%03d.jpg
	rm ${dir}/${filename}
	for j in $(ls ${dir}/*.jpg)
		do
		identify $j | grep -v -q  1024x1024 && rm $j
		done
	for j in $(ls ${dir}/*.jpg)
		do
		exiftool -overwrite_original -all= ${j} 
		done
	standalone_uid.py predict_dir -n -t ${dir}
		
	for j in $(ls ${dir}/*.svg)
	do
	my_s3cmd sync $j s3://pollen-id/to_annotate/$(basename $j)
	done
	
	rm -r ${dir}
done
