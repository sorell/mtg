#!/bin/sh

# Convert Moxfield csv to txt


if [ "`cat $1 | head -n 1 | cut -d, -f1`" != "\"Count\"" ]; then
	>&2 echo "Not a moxfield export"
	exit 1
fi

cat $1 | tail -n +2 | while read line; do
	echo -n `echo $line | cut -d\" -f2`
	echo -n " "
	echo $line | cut -d\" -f6

done
