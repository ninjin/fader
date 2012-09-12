#!/usr/bin/env python

'''
Generate token representations using lexical resources.

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2012-09-12
'''

from __future__ import print_function

from argparse import ArgumentParser, FileType
from collections import defaultdict
from datetime import datetime, timedelta
from os.path import dirname, join as path_join
from sys import path as sys_path, stderr, stdin, stdout

### Constants
SIMSTRING_PY_DIR = path_join(dirname(__file__),
        '../ext/simstring/swig/python')
###

def _argparser():
    argparser = ArgumentParser(
            'Generate token representations using lexical resources')

    argparser.add_argument('resources', nargs='+', help='lexical resources')

    argparser.add_argument('-i', '--input', type=FileType('r'),
            default=stdin, help='input file (default: stdin)')
    argparser.add_argument('-o', '--output', type=FileType('w'),
            default=stdout, help='output file (default: stdout)')
    argparser.add_argument('-e', '--input-encoding', default='utf-8',
            help='input encoding (default: utf-8)')
    argparser.add_argument('-s', '--simstring-dbs',
            help='treat lexical resources as paths to SimString databases')
    argparser.add_argument('-v', '--verbose', action='store_true',
            help='enable additional system output on stderr')
    # TODO: Caching flag
    # TODO: Iterate over tokens first flag (performance hit though...)
    # TODO: Allow to create db;s in a temp dir or specified to keep
    # TODO: Allow for various metrics
    # TODO: Specify thresholds
    return argparser

def _vprint(msg, no_tag=False, end='\n'):
    if not no_tag:
        to_print = 'VERBOSE: {}'.format(msg)
    else:
        to_print = msg
    print(to_print, file=stderr, end=end)

# This is our naive in-efficient solution until we get around to either
# extending or re-implementing SimString
def _find_threshold(query, reader, start=1.0, end=0.1, step=0.1):
    # Sanity checking, if any of these fail we won't terminate
    assert start > end
    assert step > 0

    curr_threshold = start
    while curr_threshold >= end:
        reader.threshold = curr_threshold
        if reader.retrieve(query):
            return curr_threshold
        curr_threshold -= step
    # We failed to get find any match
    return 0.0

def _token_reprs(tokens, db_paths, verbose=False):
    from simstring import cosine as simstring_cosine
    from simstring import reader as simstring_reader

    if verbose:
        db_timings = []

    repr_by_token = defaultdict(list)
    for db_path_i, db_path in enumerate(db_paths, start=1):
        if verbose:
            db_timing_start = datetime.utcnow()
            _vprint('Opening DB ({}/{}): {}'.format(db_path_i, len(db_paths),
                db_path))

        reader = simstring_reader(db_path)
        reader.measure = simstring_cosine

        if verbose:
            _vprint('Querying DB...', end='')

        for token_i, token in enumerate(tokens, start=1):
            if verbose and token_i % 1000 == 0:
               _vprint('{}...'.format(token_i), no_tag=True, end='')

            # Fech the threshold to use as a distance
            repr_by_token[token].append(_find_threshold(token.encode('utf-8'),
                reader))

        if verbose:
            _vprint('{}...Done!'.format(token_i), no_tag=True)

            db_timings.append(datetime.utcnow() - db_timing_start)
            if db_path_i != len(db_paths):
                per_db_estimate = (sum(db_timings, timedelta())
                        / len(db_timings))
                completion_estimate = (per_db_estimate
                        * (len(db_paths) - db_path_i))
                _vprint('Estimated time until completion: {}'.format(
                    completion_estimate))

    for token in tokens:
        yield token, repr_by_token[token]

def main(args):
    argp = _argparser().parse_args(args[1:])

    try:
        # At first, try using global installs
        import simstring
        del simstring
    except ImportError:
        # If that fails, try our local version
        sys_path.append(SIMSTRING_PY_DIR)
        try:
            import simstring
            del simstring
        except ImportError:
            from sys import stderr
            print('ERROR: Failed to import SimString, did you run make to '
                    'build it or install it globally?', file=stderr)
            return -1

    if not argp.simstring_dbs:
        raise NotImplementedError
    else:
        db_paths = argp.resources

    tokens = [unicode(l, encoding=argp.input_encoding).rstrip('\n')
            for l in argp.input]
    for token, repr in _token_reprs(tokens, db_paths, verbose=argp.verbose):
        print('{}\t{}'.format(token, '\t'.join(str(r) for r in repr)),
                file=argp.output)

    return 0

if __name__ == '__main__':
    from sys import argv
    exit(main(argv))
