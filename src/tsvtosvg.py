#!/usr/bin/env python

'''
Render 2D TSV output from t-SNE as an SVG.

Author:
Version:    2012-09-13
'''

# TODO: Embed CSS?

from argparse import ArgumentParser, FileType
from collections import namedtuple
from sys import stdin, stdout
from xml.sax.saxutils import escape as xml_escape

### Constants
NICE_COLOURS = (
    'black',
    'red',
    'blue',
    'orange',
    'green',
    'purple')
###

def _argparser():
    argparser = ArgumentParser('Render t-SNE output as SVG')
    argparser.add_argument('-i', '--input', type=FileType('r'), default=stdin,
            help='input source (default: stdin)')
    argparser.add_argument('-o', '--output', type=FileType('w'), default=stdout,
            help='output (default: stdout)')
    argparser.add_argument('-w', '--width',  type=int, default=4096,
            help='SVG width')
    argparser.add_argument('-e', '--height',  type=int, default=4096,
            help='SVG height')
    argparser.add_argument('-b', '--border',  type=int, default=64,
            help='SVG border where no labels are placed')
    argparser.add_argument('-c', '--colour', action='store_true',
            help=('interpret the second column as a type identifier and '
                'assign colours by type'))
    # TODO: Font size?
    return argparser

def main(args):
    argp = _argparser().parse_args(args[1:])

    argp.output.write('\n'.join(('<?xml version="1.0" encoding="UTF-8" '
                'standalone="no"?>',
            '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" '
                '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">',
            ('<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
                'style="width: {}px; height: {}px;">'
                ).format(argp.width, argp.height))))
    argp.output.write('\n')

    cats_seen = []
    for line in (l.rstrip('\n') for l in argp.input):
        if not argp.colour:
            label, x_str, y_str = line.split('\t')
            cat = 'Dummy'
        else:
            label, cat, x_str, y_str = line.split('\t')

        x_pos = argp.border + (argp.width - 2 * argp.border) * float(x_str)
        y_pos = argp.border + (argp.height - 2 * argp.border) * float(y_str)

        if cat not in cats_seen:
            cats_seen.append(cat)
        argp.output.write('\t')
        argp.output.write(('<text text-anchor="middle" x="{}" y="{}" '
            'style="fill: {};">{}</text>'
            ).format(x_pos, y_pos, NICE_COLOURS[cats_seen.index(cat)],
                xml_escape(label)))
        argp.output.write('\n')

    argp.output.write('</svg>\n')

    return 0

if __name__ == '__main__':
    from sys import argv
    exit(main(argv))
