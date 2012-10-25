#!/bin/sh

# Extract and count the matrix elements for a word representation tsv-file.
#
# Note: Just a short-hand really
#
# Author:   Pontus Stenetorp    <pontus stenetorp se>
# Version:  2012-10-23

cut -f 2- $* \
    | tr '\t' '\n' \
    | sort | uniq -c \
    | sed -e 's|^ \+||g' \
    | awk '{ print $2 "\t" $1 }' \
    | sort -n
