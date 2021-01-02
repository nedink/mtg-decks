#!/usr/bin/env python3

import argparse
import os
import requests
import time
import csv
import sys

GO_BACK_1000 = '\033[1000D'
ERASE_TO_END = '\033[K'
GO_UP_1 = '\033[1A'

scryfall_url = 'https://api.scryfall.com/'
collection_url = scryfall_url + 'cards/collection'

# def get_card(card_id):
#     response = requests.get(scryfall_url + 'cards/{card_id}')
#     if not response.ok():
#         print('Error - Could not connect to Scryfall.')
#         exit(1)
#     return response.json()

# set up parser
parser = argparse.ArgumentParser()
parser.add_argument('input_filename')
parser.add_argument('output_filename')
parser.add_argument('--overwrite', action='store_true')
parser.add_argument('-ft', '--from-type', dest='from_type', choices=['cardcastle', 'mtg-decks'], default='cardcastle')
parser.add_argument('-tt', '--to-type', dest='to_type', choices=['cardcastle', 'mtg-decks'], default='mtg-decks')
args = parser.parse_args()

# check input file exists
if not os.path.exists(args.input_filename):
    print('Error - File \'%s\' does not exist.' % args.input_filename)
    exit(1)

# check output file does not exist
if not args.overwrite and os.path.exists(args.output_filename):
    print('Error - File \'%s\' already exists. Use \'--overwrite\' to overwrite it.' % args.output_filename)
    exit(1)

# open input file
# TODO - assume different types than csv
input_file_csv = csv.reader(open(args.input_filename, 'r'))
lines = list(input_file_csv)
# if args.from_type == 'cardcastle':
#     csv_input_file

# dialect = csv.Sniffer().sniff(input_file)
# with open(args.input_filename, newline='') as csv_input_file:
#     input_reader = csv.reader(csv_input_file)
#     for index, row in enumerate(input_reader):
#         print(str(index) + ' ' + str(row))
# csv_input_file = csv.reader(input_file)
# print(csv_input_file)
# dialect.

# input_file_csv.close()

sys.stdout.write('\n')

# read + request from scryfall
identifiers = []
cards = []
not_found = []

for index, row in enumerate(lines):
    if index == 0 or not row: # skip first line
        continue
    if args.from_type == 'cardcastle':
        # get last value (card id)
        identifiers.append({
            'id': row[6][:36]
        })
        # if 75 identifiers, make scryfall request
        # print(len(lines))
        if len(identifiers) == 75 or index == len(lines) - 1:
            sys.stdout.write(GO_UP_1 + GO_BACK_1000 + ERASE_TO_END + 'Processing [' + '=' * round(index / len(lines) * 78) + '-' * round(78 - index / len(lines) * 78) + ']\n')
            sys.stdout.flush()
            # print({'identifiers': identifiers})
            response = requests.post(collection_url, json={'identifiers': identifiers})
            if not response.ok:
                print(response.json())
                exit(1)
            cards += response.json()['data']
            not_found = response.json()['not_found']
            # sleep 0.1s between requests
            if len(identifiers) == 75: 
                time.sleep(0.1)
            identifiers.clear()
            # print(cards)

# open output file
output_file = open(args.output_filename, 'w')

# write to output file
for card in cards:
    if args.to_type == 'mtg-decks':
        output_file.write('%s/%s\n' % (card['set'], card['collector_number']))

output_file.close()
