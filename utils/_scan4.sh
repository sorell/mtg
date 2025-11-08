#!/bin/sh

cat $2 | cut -f 2- | cut -d\  -f 1- | while read x ; do echo "-- LOOKING FOR $x --"; grep "$x" $1 ; done
