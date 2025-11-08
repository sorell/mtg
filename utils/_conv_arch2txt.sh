#!/bin/sh

# Convert Archidekt csv to Moxfield csv
# Expects only Quantity and Card Name

if [ "`cat $1 | tail -n +2 | head -n 1`" != "Quantity,Name" ]; then
	>&2 echo "Not an Archidekt export"
	exit 1
fi

echo TBD
exit 1
