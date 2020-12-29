#!/usr/bin/env python3

import requests
import functools
import argparse
import os.path
import re
import sys
import time
import random

RESET = '\033[0m'

BLACK = '\033[0;30m'
RED = '\033[0;31m'
GREEN = '\033[0;32m'
WHITE = '\u001b[0;37m'
BLUE = '\033[0;34m'
GRAY = '\033[0;47m'

SILVER = '\033[38;5;159m'
GOLD = '\033[38;5;220m'
ORANGE = '\033[38;5;208m'

INVERT = '\033[7m'

BLACK_BACKGROUND = '\033[40m'
RED_BACKGROUND = '\033[41m'
GREEN_BACKGROUND = '\033[42m'
YELLOW_BACKGROUND = '\033[43m'
BLUE_BACKGROUND = '\033[44m'
PURPLE_BACKGROUND = '\033[45m'
CYAN_BACKGROUND = '\033[46m'
WHITE_BACKGROUND = '\033[47m'
DEFAULT_BACKGROUND = '\033[49m'

GO_BACK_100 = '\033[100Dm'

color_map = {
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
    '8': DEFAULT_BACKGROUND,
    '9': DEFAULT_BACKGROUND,
    '10': DEFAULT_BACKGROUND,
}

mana_graph_map = {
    'W': '▇',
    'U': '▇',
    'B': '▇',
    'R': '▇',
    'G': '▇',
    '0': '0',
    '1': '▇',
    '2': '▇▇',
    '3': '▇▇▇',
    '4': '▇▇▇▇',
    '5': '▇▇▇▇▇',
    '6': '▇▇▇▇▇▇',
    '7': '▇▇▇▇▇▇▇',
    '8': '▇▇▇▇▇▇▇▇',
    '9': '▇▇▇▇▇▇▇▇▇',
    '10': '▇▇▇▇▇▇▇▇▇▇',
}

oracle_symbol_map = {
    '{W}': RED + '▉' + RESET,
    '{U}': BLUE + '▉' + RESET,
    '{B}': BLACK + '▉' + RESET,
    '{R}': RED + '▉' + RESET,
    '{G}': GREEN + '▉' + RESET,
    '{1}': INVERT + '1' + RESET,
    '{2}': INVERT + '2' + RESET,
    '{3}': INVERT + '3' + RESET,
    '{4}': INVERT + '4' + RESET,
    '{5}': INVERT + '5' + RESET,
    '{6}': INVERT + '6' + RESET,
    '{7}': INVERT + '7' + RESET,
    '{8}': INVERT + '8' + RESET,
    '{9}': INVERT + '9' + RESET,
    '{10}': INVERT + '10' + RESET,
}

loading_spinner = [
    '/', '-', '\\', '|'
]
loading_spinner_index = 0

scryfall_url = 'https://api.scryfall.com/cards/collection'

# set up parser
parser = argparse.ArgumentParser()
parser.add_argument('filename')
parser.add_argument('-o', '--order-by', dest='orderBy')
# parser.add_argument('-f', '--filter-by', dest='filterBy')
parser.add_argument('-c', '--color', dest='colors', action='append')
parser.add_argument('-w', '--word', dest='words', action='append')
parser.add_argument('-t', '--oracle-text', dest='oracleText', action='store_true')
parser.add_argument('-M', '--modify', dest='modify', action='store_true')
args = parser.parse_args()

# get file name
filename = args.filename

# check file exists
if not os.path.exists(filename):
    print('file \'' + filename + '\' does not exist.')
    exit(1)

# open file
fo = open(filename, 'r+')
lines = fo.read().splitlines()

# for each line...
identifiers = []
cards = []
notFound = []
for index, line in enumerate(lines, start=1):
    # if correct format...
    if re.match('[a-zA-Z0-9]+/[0-9]+', line):
        split = line.split('/')
        # create identifier
        if len(split) == 2 and len(split[0]) > 0 and len(split[1]) > 0: 
            identifiers.append({
                'set': split[0].lower(),
                'collector_number': str(int(split[1]))
            })
    # request cards from scryfall
    if len(identifiers) > 0 and len(identifiers) == 75 or index == len(lines):
        response = requests.post(scryfall_url, json={'identifiers': identifiers})
        if not response.ok:
            print(response.json()['details'])
            exit(1)
        cards += response.json()['data']
        notFound = response.json()['not_found']
        # sleep 0.1s between requests
        if len(identifiers) == 75: 
            time.sleep(0.1)
        identifiers.clear()

# pre-sort modification
for card in cards:
    if 'power' in card:
        try:
            card['power'] = float(card['power'])
        except ValueError:
            card['power'] = float(0)
    if 'toughness' in card:
        try:
            card['toughness'] = float(card['toughness'])
        except ValueError:
            card['toughness'] = float(0)

# sort cards (--order-by)
cards = sorted(cards, key=lambda card: 0 if not args.orderBy else 0 if not args.orderBy in card else card[args.orderBy] if isinstance(card[args.orderBy], int) or isinstance(card[args.orderBy], float) else card[args.orderBy].lower() if isinstance(card[args.orderBy], str) else len(card[args.orderBy]) if isinstance(card[args.orderBy], list) else 0)
# try:
# except TypeError:
    
# cards = sorted(cards, key=sort_cards)

# modify file (--modify-file)
if args.modify and len(notFound) == 0:
    deckstr = functools.reduce(lambda c1, c2: c1 + c2['set'] + '/' + c2['collector_number'] + '\n', cards, '')
    fo.seek(0)
    fo.write(deckstr)
    fo.truncate(len(deckstr))

# close file
fo.close()

# trim word
for card in cards:
    card['name'] += ' '
    if len(card['name']) > 32:
        card['name'] = card['name'][:29] + '...'
    card['type_line'] += ' '
    if len(card['type_line']) > 32:
        card['type_line'] = card['type_line'][:29] + '...'

    # todo - handle card_faces case better
    if 'card_faces' in card:
        card['mana_cost'] = functools.reduce(lambda c1, c2: c1 + c2['mana_cost'], card['card_faces'], '')
        # print(card['mana_cost'])
    
    # todo - this is a test
    # if card['name'] == 'Apex Devastator':
        # print(card['mana_cost'])
    
    # parse mana_cost
    matches = re.findall('\\{([WUBRG/0-9])+\\}', card['mana_cost'])
    if len(matches) > 0:
        card['manaDisplay'] = functools.reduce(lambda s1, s2: s1 + str(color_map.get(s2)) + str(mana_graph_map.get(s2)) + RESET, matches, '')
    else:
        card['manaDisplay'] = ''
    card['manaDisplay'] += ' ' * int(16 - card['cmc'])
    
    if card['rarity'] == 'common':
        card['rarity'] = ''
    if card['rarity'] == 'uncommon':
        card['rarity'] = SILVER
    if card['rarity'] == 'rare':
        card['rarity'] = GOLD
    if card['rarity'] == 'mythic':
        card['rarity'] = ORANGE

# Console display - cards 
card_index = next_index = 0
def reduce(c1, c2):
    global card_index, next_index
    next_index += 1
    next_index = min(next_index, len(cards) - 1)

    cardCodeCol = (c2['set'] + '/' + c2['collector_number']).ljust(8)
    nameCol = c2['name'].ljust(32, '─' if index % 2 == 0 else '─')
    typeLineCol = c2['type_line'].ljust(32, '─' if index % 2 == 0 else '─')
    cmcCol = (str(int(c2['cmc'])) if c2['cmc'] % 1 == 0 else str(c2['cmc'])).ljust(2)
    rarity = c2['rarity']
    oracleText = c2['oracle_text'].replace('\n', ' ') if args.oracleText else ''
    for key in oracle_symbol_map:
        oracleText = oracleText.replace(key, oracle_symbol_map[key])
    
    # extra line break between types if ordering by type_line
    extraLineBreak = (('\n' if index > 0 and c2['type_line'].split('—')[0].strip() != cards[next_index]['type_line'].split('—')[0].strip() else '') if args.orderBy == 'type_line' else '')
    
    # check for filtered colors (card identity must include ANY)
    hasFilteredColors = not args.colors
    if args.colors and cards[card_index]['color_identity']:
        for color in args.colors:
            if color.upper() in cards[card_index]['color_identity']:
                hasFilteredColors = True
    
    # check for filtered words (card text must include ALL)
    hasFilteredWords = True
    if args.words:
        for word in args.words:
            if not word.lower() in cards[card_index]['type_line'].lower() and not word.lower() in cards[card_index]['oracle_text']:
                hasFilteredWords = False
    
    # create the would-be line of console output
    card_line = c1 + rarity + cardCodeCol + '  ' + nameCol + '  ' + typeLineCol + '  ' + cmcCol + '  ' + RESET + c2['manaDisplay'] + oracleText + extraLineBreak + '\n'

    card_index += 1
    
    # show card unless it does not fit filter criteria
    return card_line if hasFilteredColors and hasFilteredWords else c1

deckPrintStr = functools.reduce(reduce, cards, '')

print('\n' + str(len(cards)) + ' cards\n-------')

print(deckPrintStr, end='')

print('-------\nMana curve')
for i in range(0, 10):
    mana_cost = 0
    for c in cards:
        if not re.search('Land', c['type_line']) and round(c['cmc']) == i:
            mana_cost += 1
    # get the cards with cmc == i AND NOT land
    # print '▇' that many times
    print(str(i) + ' ' + INVERT + (str(mana_cost) if mana_cost else '') + (' ' * (mana_cost - len(str(mana_cost)))) + RESET)
mana_cost = 0
for c in cards:
    if not re.search('Land', c['type_line']) and c['cmc'] >= 10:
        mana_cost += 1
print('+ ' + INVERT + (str(mana_cost) if mana_cost else '') + (' ' * (mana_cost - len(str(mana_cost)))) + RESET)



print('-------\n' + str(len(cards)) + ' cards')

if not len(notFound) == 0:
    print('File not modifed. Unknown identifiers: ' + str(functools.reduce(lambda i1, i2: i1 + (', ' if len(i1) > 0 else '') + '\'' + i2['set'] + '/' + i2['collector_number'] + '\'', notFound, '')))
