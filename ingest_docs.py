#!/usr/bin/env python3
import argparse
from lib.ingest import *

def main():
	args = parse_arguments()
	i = Ingest(profile=args.profile, db=args.db)
	i.run()

def parse_arguments():
	parser = argparse.ArgumentParser(description='AIDE: Ask questions to your documents without an internet connection, using the power of LLMs.')
	parser.add_argument("--profile", "-p", default='main', help='Select profile.')
	parser.add_argument("--db", "-d", default='main', help='Select db.')

	args = parser.parse_args()
	if 'help' in args :
		parser.print_help()
		exit()
	return args

if __name__ == "__main__":
	main()
