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

BLACK_BACKGROUND = "\033[40m"
RED_BACKGROUND = "\033[41m"
GREEN_BACKGROUND = "\033[42m"
YELLOW_BACKGROUND = "\033[43m"
BLUE_BACKGROUND = "\033[44m"
PURPLE_BACKGROUND = "\033[45m"
CYAN_BACKGROUND = "\033[46m"
WHITE_BACKGROUND = "\033[47m"
DEFAULT_BACKGROUND = "\033[49m"


colorMap = {
    'W': WHITE,
    'U': BLUE,
    'B': BLACK,
    'R': RED,
    'G': GREEN,
    '0': DEFAULT_BACKGROUND,
    '1': DEFAULT_BACKGROUND,
    '2': DEFAULT_BACKGROUND,
    '3': DEFAULT_BACKGROUND,
    '4': DEFAULT_BACKGROUND,
    '5': DEFAULT_BACKGROUND,
    '6': DEFAULT_BACKGROUND,
    '7': DEFAULT_BACKGROUND,
}

symbolMap = {
    'W': '▊',
    'U': '▊',
    'B': '▊',
    'R': '▊',
    'G': '▊',
    '0': '0',
    '1': '▊',
    '2': '█▊',
    '3': '██▊',
    '4': '███▊',
    '5': '████▊',
    '6': '█████▊',
    '7': '██████▊',
    '8': '███████▊',
    '9': '████████▊',
    '10': '█████████▊',
}

# def manaColorMap(symbol):
#     for key in colorMap.keys():
#         match = re.match(key, symbol)
#         if match:
            
#             return colorMap.get(symbol)
#     return symbol

URL = 'https://api.scryfall.com/cards/collection'

parser = argparse.ArgumentParser()
parser.add_argument('filename')
parser.add_argument('-o', '--order-by', dest='orderBy', default='cmc')
parser.add_argument('-t', '--oracle-text', dest='oracleText')
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
cards = sorted(cards, key=lambda card: card[args.orderBy] if card[args.orderBy] is int or float else card[args.orderBy].lower() if card[args.orderBy] is str else len(card[args.orderBy]))

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
        card['name'] = card['name'][:29] + '...'
    card['type_line'] += ' '
    if len(card['type_line']) > 32:
        card['type_line'] = card['type_line'][:29] + '...'
    # m = re.search('\\{[WUBRG]\\}', card['mana_cost'])

    matches = re.findall('\\{([WUBRG/0-9])+\\}', card['mana_cost'])
    # print(matches)
    if len(matches) > 0:
        card['manaDisplay'] = functools.reduce(lambda s1, s2: s1 + colorMap.get(s2) + symbolMap.get(s2) + RESET, matches, '')
    else:
        card['manaDisplay'] = ''

deckPrintStr = functools.reduce(lambda c1, c2: c1 + c2['set'] + '/' + c2['collector_number'] + '  ' + ' ' * (5 - len(c2['color_identity'])) + functools.reduce(lambda i1, i2: i1 + colorMap.get(i2) + '█' , c2['color_identity'], '') + '  ' + RESET + c2['name'].ljust(32, '_') + '  ' + c2['type_line'].ljust(32, '_') + '  ' + (str(int(c2['cmc'])) if c2['cmc'] % 1 == 0 else str(c2['cmc'])).ljust(5) + c2['manaDisplay'].ljust(32) + '\n', cards, '')
print(deckPrintStr + '-------\n' + str(len(cards)) + ' cards')
if not len(notFound) == 0:
    print('File not modifed. Unknown identifiers: ' + str(functools.reduce(lambda i1, i2: i1 + (', ' if len(i1) > 0 else '') + '\'' + i2['set'] + '/' + i2['collector_number'] + '\'', notFound, '')))
