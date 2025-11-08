#!/usr/bin/python3

import sys
import re
import itertools

# Convert CT wishlist copy-paste to excel
# Expects only card name and price

# File looks like this:
# 0/19 selected
# Filter by card name or set

# 1
# Akroma's Will
# Akroma's Will

# M3C - Commander: Modern Horizons 3 #165

# EN

# Moderately Played

# Any
# €12.49 

# 1
# Apex Devastator
# Apex Devastator


priceOnly = False
try:
	del sys.argv[sys.argv.index('-p')]
	priceOnly = True
except:
	pass

with open(sys.argv[1]) as copyPasteFile:
	chunk = copyPasteFile.readlines()

# Drop all until get line like
# 1
nrOfCardsPattern = re.compile('^[0-9]*$')
chunk = list(itertools.dropwhile(lambda elem: not nrOfCardsPattern.match(elem), chunk))

# Remove newline characters and empty elements
chunk = [elem.strip() for elem in chunk]
chunk = list(filter(lambda elem: elem != '', chunk))

# The chunk looks like:
# '1', "Akroma's Will", "Akroma's Will", 'M3C - Commander: Modern Horizons 3 #165', 'EN', 'Moderately Played', 'Any', '€12.49', '1', 'Apex Devastator'
# Get indexes of number of cards and indexes of prices, ie '1' and '€12.49' from the first card above 
nrOfCardsIndexes = [idx for idx, elem in enumerate(chunk) if nrOfCardsPattern.match(elem)]
priceIndexes = [idx for idx, elem in enumerate(chunk) if elem[0] == '€']

if len(nrOfCardsIndexes) != len(priceIndexes):
	raise Exception('Number of cards don\'t match number of prices')

# First remove elements between card name and price, second remove card count
for i in range(len(nrOfCardsIndexes)-1, -1, -1):
	#print('nrOfCardsIndexes', nrOfCardsIndexes[i], chunk[nrOfCardsIndexes[i]])
	#print('priceIndexes', priceIndexes[i], chunk[priceIndexes[i]])
	del chunk[nrOfCardsIndexes[i]+2:priceIndexes[i]]
	del chunk[nrOfCardsIndexes[i]]

# Print out card name; price without €
for i in range(0, len(chunk), 2):
	print('%s%s' % ('' if priceOnly else ("%s; " % chunk[i]), chunk[i+1][1:]))
