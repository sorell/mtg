#!/bin/sh

# Convert Dragon Shield csv to Moxfield csv

# Could not find card named "Wolfwillow Haven" in edition "PTHB". on line 155
# PTHB -> thb

# Could not find card named "Oros, the Avenger" in edition "PPRE". on line 60
# PPRE -> pplc

if [ "`cat $1 | tail -n +2 | head -n 1 | cut -d, -f1`" != "Folder Name" ]; then
	>&2 echo "Not a dragon shield export"
	exit 1
fi

echo '"Count","Tradelist Count","Name","Edition","Condition","Language","Foil","Tags","Last Modified","Collector Number","Alter","Proxy","Purchase Price"'

cat $1 | tail -n +3 | while read line; do

	# Number of cards
	echo -n '"'
	echo -n `echo $line | cut -d, -f2`
	echo -n '","0","'

	# The card name can be in quotation marks, which breaks cutting with ,
	name=`echo $line | cut -d, -f4`
	rest=`echo $line | cut -d, -f5-`
	if echo $name | grep -q \"; then
		name=`echo $line | cut -d\" -f2`
		rest=`echo $line | cut -d\" -f3- | cut -b2-`
	fi

	# Name of the card
	echo -n $name'","'

	# Name of the set shorthand
	echo -n `echo $rest | cut -d, -f1`
	echo -n '","","'

	# The set long name can be in quotation marks, which breaks cutting with ,
	setName=`echo $rest | cut -d, -f2`
	if echo $setName | cut -d, -f1 | grep -q \"; then
		rest=`echo $rest | cut -d\" -f3- | cut -b2-`
	else
		rest=`echo $rest | cut -d, -f3- `
	fi
	
	# Card number
	num=`echo $rest | cut -d, -f1`

	# Foil/normal
	foil=`echo $rest | cut -d, -f3`

	# Language
	echo -n `echo $rest | cut -d, -f4`
	echo '","'$foil'","","'`date +"%F %T.000000"`'","'$num'","False","False",""'

done
