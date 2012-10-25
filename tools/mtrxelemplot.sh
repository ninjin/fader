#!/bin/sh

# Analyse the distribution of matrix values.
#
# Author:   Pontus Stenetorp    <pontus stenetorp se>
# Version:  2012-10-23

# TODO: Check that we have arguments

CMD=''
for e in $*
do
    CMD="${CMD}, '< tools/mtrxelemstats.sh ${e} | tools/thresbuckets.sh' with linespoints"
done

echo "${CMD}" | sed -e 's|^,|plot|g' | gnuplot --persist

