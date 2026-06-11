#!/usr/bin/env python3
"""
Strip comments and docstrings from a file.

Copied from https://gist.github.com/BroHui/aca2b8e6e6bdf3cb4af4b246c9837fa3 with modifications.
"""

import sys, token, tokenize


def process_file(infile, outfile):
    """
    Remove comments and docstrings from one file and write the result to another.

    @param infile   The path to the file to process
    @param outfile  The path to the file we're generating
    """
    source = open(infile, "r")
    mod = open(outfile, "w")

    prev_toktype = token.INDENT
    last_lineno = -1
    last_col = 0

    tokgen = tokenize.generate_tokens(source.readline)
    for toktype, ttext, (slineno, scol), (elineno, ecol), ltext in tokgen:
        if 0:   # Change to if 1 to see the tokens fly by.
            print("%10s %-14s %-20r %r" % (
                tokenize.tok_name.get(toktype, toktype),
                "%d.%d-%d.%d" % (slineno, scol, elineno, ecol),
                ttext, ltext
                ))
        if slineno > last_lineno:
            last_col = 0
        if scol > last_col:
            mod.write(" " * (scol - last_col))
        if toktype == token.STRING and prev_toktype == token.INDENT:
            # Docstring
            mod.write("#--")
        elif toktype == tokenize.COMMENT:
            # Comment
            mod.write("##")
        else:
            mod.write(ttext)
        prev_toktype = toktype
        last_col = ecol
        last_lineno = elineno


if __name__ == '__main__':
    process_file(sys.argv[1], sys.argv[2])
