#!/bin/sh

# Bucket mtrxelemstats.sh output into thresholds.
#
# Note: If you know how to do this from within gnuplot, do tell me.
#
# Author:   Pontus Stenetorp    <pontus stenetorp se>
# Version:  2012-10-25

awk '{ printf "%.1f\t%d\n", int($1 * 10) / 10, $2 }' \
    | awk '{ cnt[$1]+=$2 } END { for (k in cnt) { print k, cnt[k] } }' \
    | sort -n
