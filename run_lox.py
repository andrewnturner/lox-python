import argparse

from lox import Lox

parser = argparse.ArgumentParser()
parser.add_argument('path', nargs='?', default=None)
args = parser.parse_args()

lox = Lox()

if args.path is not None:
    lox.run_file(args.path)
else:
    lox.run_prompt()