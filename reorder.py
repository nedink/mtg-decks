#!/usr/local/anaconda3/bin/python

import requests
import functools
import argparse
import os.path
import re

RESET = '\033[0m'
BLACK = '\033[0;30m'
RED = '\033[0;31m'
GREEN = '\033[0;32m'
WHITE = '\u001b[0;37m'
BLUE = '\033[0;34m'
GRAY = '\033[0;47m'

manaColorMap = {
    '\\{W\\}': WHITE,
    '\\{U\\}': BLUE,
    '\\{B\\}': BLACK,
    '\\{R\\}': RED,
    '\\{G\\}': GREEN,
    '\\{\\d\\}': GRAY,
}

URL = 'https://api.scryfall.com/cards/collection'

parser = argparse.ArgumentParser()
parser.add_argument('filename')
parser.add_argument('-o', '--order-by', dest='orderBy', default='cmc')
parser.add_argument('-m', '--modify-file', dest='modify', action='store_true')
args = parser.parse_args()
filename = args.filename

if not os.path.exists(filename):
    print('file \'' + filename + '\' does not exist.')
    exit(1)

fo = open(filename, 'r+')
lines = fo.read().splitlines()
identifiers = []
cards = []
for index, line in enumerate(lines, start=1):
    split = line.split('/')
    if len(split) == 2 and len(split[0]) > 0 and len(split[1]) > 0: 
        identifiers.append({
            'set': split[0],
            'collector_number': split[1]
        })
    if len(identifiers) > 0 and len(identifiers) == 75 or index == len(lines):
        response = requests.post(URL, json={'identifiers': identifiers})
        if not response.ok:
            print(response.text)
            exit(1)
        cards = response.json()['data']
        notFound = response.json()['not_found']
        identifiers.clear()

cards = sorted(cards, key=lambda card: card[args.orderBy])

# reorder deck in file
if args.modify and len(notFound) == 0:
    deckstr = functools.reduce(lambda c1, c2: c1 + c2['set'] + '/' + c2['collector_number'] + '\n', cards, '')
    fo.seek(0)
    fo.write(deckstr)
    fo.truncate(len(deckstr))
fo.close()
# trim word

for card in cards:
    card['name'] += ' '
    if len(card['name']) > 32:
        card['name'] = card['name'][:13] + '...'
    card['type_line'] += ' '
    if len(card['type_line']) > 32:
        card['type_line'] = card['type_line'][:13] + '...'
    m = re.search('\\{[WUBRG]\\}', card['mana_cost'])
    # if len(m.groups()) > 
    # mana = m.group(0)

    mana = re.findall('\\{[WUBRG/0-9]+?\\}', card['mana_cost'])
    # groups = []
    # if mana != None:
    #     groups = mana.groups()
    #     for m in groups:
    #         if m != None:
    #             m.strip('\\{|\\}|\\[|\\]|\\,|\\\'')
    #         else:
    #             m = ''
    # else:
    #     mana = ''
    # print(str(groups))

    print(mana)

    # mana = re.findall('\\{([WUBRG](/[WUBRG])?)?\\}', card['mana_cost'])
    # for m in mana:
    #     m.strip('\\{|\\}|\\[|\\]|\\\,|\\\'')
    # print(mana)


deckPrintStr = functools.reduce(lambda c1, c2: c1 + c2['set'] + '/' + c2['collector_number'] + '  ' + c2['name'].ljust(32, '.') + '  ' + c2['type_line'].ljust(32, '.') + '  ' +  c2['mana_cost'].ljust(32, '.') + '\n', cards, '')
print(deckPrintStr + '-------\n' + str(len(cards)) + ' cards')
if not len(notFound) == 0:
    print('File not modifed. Unknown identifiers: ' + str(functools.reduce(lambda i1, i2: i1 + (', ' if len(i1) > 0 else '') + '\'' + i2['set'] + '/' + i2['collector_number'] + '\'', notFound, '')))
