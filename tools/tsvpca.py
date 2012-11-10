#!/usr/bin/env python

'''
Perform Principal Component Analysis for TSV input using Scikit-learn.

From: http://scikit-learn.org/stable/install.html

    apt-get install python-sklearn

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2012-09-13
'''

from __future__ import print_function

from argparse import ArgumentParser, FileType
from collections import defaultdict
from math import sqrt
from sys import stderr, stdin, stdout

from numpy.linalg import svd
from scipy.sparse import dok_matrix
from sklearn.decomposition import PCA, RandomizedPCA

def _argparser():
    argparser = ArgumentParser('PCA for TSV input using Scikit-learn')

    argparser.add_argument('-i', '--input', type=FileType('r'), default=stdin,
            help='input source (default: stdin)')
    argparser.add_argument('-o', '--output', type=FileType('w'), default=stdout,
            help='output (default: stdout)')
    argparser.add_argument('-d', '--dimensionality', type=int, default=2,
            help='target dimensionality')
    argparser.add_argument('-s', '--dimensionality-search',
            action='store_true', help=('Print the sorted absolute values of '
                'the co-variance matrix, can be used to determine the '
                'optimal number of dimensions'))
    argparser.add_argument('-n', '--no-normalisation', action='store_true',
            help="don't normalise the output to the range of [0,1]")
    argparser.add_argument('-p', '--sparse', action='store_true',
            help='input on the format ${COL}:${VAL} and stored sparsely')
    argparser.add_argument('-r', '--randomised-pca', action='store_true',
            help='use randomised PCA as opposed to vanilla PCA')
    return argparser

def main(args):
    argp = _argparser().parse_args(args[1:])

    # Read the data
    if argp.sparse:
        data = defaultdict(dict)
        max_col = None
    else:
        data = []

    for line_num, line in enumerate((l.rstrip('\n') for l in argp.input),
            start=1):
        if argp.sparse:
            for col, val in ((int(c), float(v)) for c, v in
                    (e.split(':') for e in line.split('\t'))):
                data[line_num - 1][col] = val
                max_col = max(max_col, col)
        else:
            try:
                data.append([float(v) for v in line.split('\t')])
            except ValueError:
                print(('ERROR: unable to read line {line_num} "{line}"'
                        ).format(line_num=line_num, line=line), file=stderr)
                return -1

    if argp.sparse:
        data_mtrx = dok_matrix((len(data), max_col + 1), dtype=float)
        for row, entries in data.iteritems():
            for col, val in entries.iteritems():
                print(row, col)
                data_mtrx[(row, col)] = val
    else:
        data_mtrx = data

    # Useful flag for analysis of optimal dimension
    if argp.dimensionality_search:
        sing_vals = svd(data_mtrx, full_matrices=0, compute_uv=False)
        prev_sing_val = None
        print('\t'.join(('Line', 'Sing. value', 'Delta', )))
        for sing_val_i, sing_val in enumerate(sorted(abs(sing_vals)), start=1):
            print('\t'.join(unicode(v) for v in (sing_val_i, sing_val,
                sing_val - prev_sing_val if prev_sing_val is not None else ''
                )))
            prev_sing_val = sing_val
        return 0

    # Run PCA
    if not argp.randomised_pca:
        pca_f = PCA
    else:
        pca_f = RandomizedPCA
    pca_conf = pca_f(n_components=argp.dimensionality, copy=False)
    res = pca_conf.fit_transform(data_mtrx)

    # Normalise the results?
    if not argp.no_normalisation:
        _, columns = res.shape
        for column in xrange(columns):
            res[:,column] -= res[:,column].min()
            res[:,column] /= res[:,column].max()

    # And print it all out...
    for row in res:
        argp.output.write('\t'.join(unicode(e) for e in row))
        argp.output.write('\n')

    return 0

if __name__ == '__main__':
    from sys import argv
    exit(main(argv))
