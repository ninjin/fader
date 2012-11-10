#!/usr/bin/env python

'''
Generate n-grams from input strings.

If you want liblinear-style feature representations, here is a nice hack:

    paste <(cut -f 1 ${FILE}) <(./ngram.py -i ${FILE} | cut -f 2- \
            | sed -e 's| |_|g' -e 's|\t|:1 |g' -e 's|$|:1|g' -e 's|\t| |g')

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2012-11-09
'''

from __future__ import print_function

from argparse import ArgumentParser, FileType
from collections import defaultdict
from itertools import chain, tee
from sys import stdin, stdout

### Constants
DEFAULT_NGRAM = 3
# Character used to represent emptiness for strings that are shorter than the
#   requested length of grams.
DEFAULT_NULL_CHAR = '~'
DEFAULT_GUARD_CHAR = '$'
###

# Generalised pairwise from the itertools recipies
def nwise(it, n):
    assert n > 1 
    its = [it]
    for _ in range(1, n):
        prev_it = its.pop()
        new_prev_it, next_it = tee(prev_it)
        next(next_it, None)
        its.extend((new_prev_it, next_it, ))
    return zip(*its)

def ngram_gen(src_str, size, guard_char=DEFAULT_GUARD_CHAR):
    if guard_char:
        left_padding = guard_char * (size - 1)
        right_padding = left_padding
    elif len(src_str) < size:
        # We need to pad the string with NULL;s to represent "nothing"
        left_padding = ''
        right_padding = DEFAULT_NULL_CHAR * (size - len(src_str))
    else:
        # No padding is necessary
        left_padding = ''
        right_padding = left_padding

    for gram in nwise(chain(left_padding, src_str, right_padding), size):
        yield ''.join(gram)

def ngram_featurise(src_str, ngram=3, guard_char=DEFAULT_GUARD_CHAR):
    feat_cnt = defaultdict(int)
    for gram in ngram_gen(src_str, size=ngram, guard_char=guard_char):
        feat_cnt[gram] += 1
        yield '{gram}#{cnt}'.format(gram=gram, cnt=feat_cnt[gram])

def _argparser():
    argparser = ArgumentParser('Generate string n-grams')
    # TODO: Doc for flags
    argparser.add_argument('-i', '--input', type=FileType('r'), default=stdin)
    argparser.add_argument('-o', '--output', type=FileType('w'),
            default=stdout)
    argparser.add_argument('-n', '--ngram', type=int, default=DEFAULT_NGRAM)
    argparser.add_argument('-u', '--null-char', type=str,
            default=DEFAULT_NULL_CHAR)
    argparser.add_argument('-g', '--guards', action='store_true')
    argparser.add_argument('-r', '--guard-char', type=str,
            default=DEFAULT_GUARD_CHAR)
    return argparser

def main(args):
    argp = _argparser().parse_args(args[1:])

    if not argp.guards:
        guard_char = ''
    else:
        guard_char = argp.guard_char

    for line in (l.rstrip('\n') for l in argp.input):
        print('{string}\t{feats}'.format(string=line, feats='\t'.join(
            ngram_featurise(line, guard_char=guard_char)), file=argp.output))

    return 0

if __name__ == '__main__':
    from sys import argv
    exit(main(argv))
