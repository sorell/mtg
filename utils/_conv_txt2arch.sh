#!/bin/sh

# Convert text to Archidekt csv
# Expects only Quantity and Card Name

if file $1 | grep -q " CRLF "; then
	echo ERROR: Windows line endings in $1
	exit 1
fi

echo "Quantity,Name"

cat $1 | tail -n +1 | while read line; do
	echo -n `echo $line | cut -d\  -f1`
	echo ',"'`echo $line | cut -d\  -f2-`'"'
done
