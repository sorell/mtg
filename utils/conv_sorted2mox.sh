#!/bin/sh

# Convert Sorted site csv to Moxfield csv

# The export starts with a "sep=," line, followed by the header
if [ "`tail -n +2 "$1" | head -n 1 | tr -d '\r'`" != "List Type,List Name,Collection,Format,Board,Quantity,Card Name,Set Code,Set Name,Card Number,Condition,Printing,Rarity,Language,Price Bought,Date Bought,Parent List Type,Parent List Name,Current Price (tcgplayer_marketsellprice),List Cover Image,Parent List Cover Image" ]; then
	>&2 echo "Not a sorted site's export"
	exit 1
fi

echo '"Count","Tradelist Count","Name","Edition","Condition","Language","Foil","Tags","Last Modified","Collector Number","Alter","Proxy","Purchase Price"'

now=`date -u +"%F %T.000000"`

tail -n +3 "$1" | tr -d '\r' | awk -v now="$now" '
# Split a csv line into f[1..n], honouring quoted fields
function parse(line,    i, c, inq, n, cur) {
	n = 1; cur = ""; inq = 0
	for (i = 1; i <= length(line); i++) {
		c = substr(line, i, 1)
		if (inq) {
			if (c == "\"") {
				if (substr(line, i + 1, 1) == "\"") { cur = cur "\""; i++ }
				else inq = 0
			} else cur = cur c
		} else if (c == "\"") inq = 1
		else if (c == ",") { f[n++] = cur; cur = "" }
		else cur = cur c
	}
	f[n] = cur
	return n
}
function q(s) { gsub(/"/, "\"\"", s); return "\"" s "\"" }
NF == 0 { next }
{
	parse($0)
	# CamelCase condition to words, e.g. NearMint -> Near Mint
	cond = f[11]
	while (match(cond, /[a-z][A-Z]/)) cond = substr(cond, 1, RSTART) " " substr(cond, RSTART + 1)
	lang = (f[14] in langs) ? langs[f[14]] : f[14]
	foil = (f[12] == "Foil") ? "foil" : ""
	# Quantity, Card Name, Set Code, Condition, Language, Printing, Card Number
	print q(f[6]) "," q(f[6]) "," q(f[7]) "," q(tolower(f[8])) "," q(cond) "," q(lang) "," q(foil) ",\"\"," q(now) "," q(f[10]) ",\"False\",\"False\",\"\""
}
BEGIN {
	langs["en"] = "English"; langs["de"] = "German"; langs["fr"] = "French"
	langs["it"] = "Italian"; langs["es"] = "Spanish"; langs["pt"] = "Portuguese"
	langs["ja"] = "Japanese"; langs["ko"] = "Korean"; langs["ru"] = "Russian"
	langs["zhs"] = "Simplified Chinese"; langs["zht"] = "Traditional Chinese"
}'
