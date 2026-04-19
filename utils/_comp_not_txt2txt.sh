#!/bin/sh

if file $1 | grep -q " CRLF "; then
	echo ERROR: Windows line endings in $1
	exit 1
fi

echo "Cards in $1 that can NOT be found in $2:"

cat $1 | while read line; do
	card=`echo $line | cut -d\  -f2-`

	if ! grep -q "$card" $2; then
		echo $line
	fi
done
