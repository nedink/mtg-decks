#!/usr/bin/env python3

import requests
import functools
import argparse
import os.path
import re
import sys
import time
import textwrap
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

def color256(index):
    return '\033[38;5;{i}'.format(index)

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

# INVERT + '▇' + RESET
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
    '{T}': INVERT + '↷' + RESET,
    '{Q}': INVERT + '↶' + RESET,
    '{PW}': INVERT + '♛' + RESET,
    '{X}': INVERT + 'X' + RESET,
    '{Y}': INVERT + 'Y' + RESET,
    '{Z}': INVERT + 'Z' + RESET,
    '{W}': RED + '▇' + RESET,
    '{U}': BLUE + '▇' + RESET,
    '{B}': BLACK + '▇' + RESET,
    '{R}': RED + '▇' + RESET,
    '{G}': GREEN + '▇' + RESET,
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

scryfall_url = 'https://api.scryfall.com/'

collection_url = scryfall_url + 'cards/collection'
word_bank_url = scryfall_url + 'catalog/word-bank'
common_word_url = 'https://gist.githubusercontent.com/nedink/629124636fc4a135b04812041c00c033/raw/c8de465c3db6a9f35affe968845b5fb9606970d1/common-mtg-words.txt'
keyword_actions_url = scryfall_url + 'catalog/keyword-actions'
keyword_abilities_url = scryfall_url + 'catalog/keyword-abilities'

# set up parser
parser = argparse.ArgumentParser()
parser.add_argument('filename')
parser.add_argument('-o', '--order-by', dest='order_by', choices=['name', 'cmc', 'type_line', 'power', 'toughness'])
parser.add_argument('-c', '--color', dest='colors', action='append', choices=['W', 'U', 'B', 'R', 'G'])
parser.add_argument('-w', '--word', dest='words', action='append')
parser.add_argument('-k', '--show-keywords', dest='show_keywords', action='store_true')
parser.add_argument('-t', '--show-text', dest='show_oracle_text', action='store_true')
parser.add_argument('-M', '--modify', dest='modify', action='store_true')
args = parser.parse_args()

# timer
start_time = time.time()

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
        time.sleep(0.1) # sleep 0.1s
        response = requests.post(collection_url, json={'identifiers': identifiers})
        if not response.ok:
            print(response.json()['details'])
            exit(1)
        cards += response.json()['data']
        notFound = response.json()['not_found']
        identifiers.clear()

if args.show_keywords:
    # request word bank from scryfall
    time.sleep(0.1) # sleep 0.1s
    response = requests.get(word_bank_url)
    if not response.ok:
        print(response.json()['details'])
        exit(1)
    word_bank = response.json()['data']
    # get common words
    common_words = requests.get(common_word_url).text.splitlines()
    # remove common words and special characters from word_bank (better fix should be implemented in future)
    word_bank = [word for word in word_bank if not word in common_words and re.fullmatch('[a-zA-Z-]+', word)]


# pre-sort card processor
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
cards = sorted(cards, key=lambda card: 0 if not args.order_by else 0 if not args.order_by in card else card[args.order_by] if isinstance(card[args.order_by], int) or isinstance(card[args.order_by], float) else card[args.order_by].lower() if isinstance(card[args.order_by], str) else len(card[args.order_by]) if isinstance(card[args.order_by], list) else 0)

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
rendered_cards = []
card_lines = []
card_index = next_index = 0
def reduce(c1, c2):
    global card_lines, card_index, next_index, word_bank
    card = cards[card_index]
    next_index += 1
    next_index = min(next_index, len(cards) - 1)
    
    cardCodeCol = (c2['set'] + '/' + c2['collector_number']).ljust(8)
    nameCol = c2['name'].ljust(32, '─' if index % 2 == 0 else '─')
    typeLineCol = c2['type_line'].ljust(32, '─' if index % 2 == 0 else '─')
    cmcCol = (str(int(c2['cmc'])) if c2['cmc'] % 1 == 0 else str(c2['cmc'])).ljust(3)
    rarity = c2['rarity']
    # word_bank
    keyword_list = [word for word in enumerate(word_bank) if re.search('\\W' + word + '\\W', card['type_line'].lower() + ' ' + card['oracle_text'].lower())] if args.show_keywords else []
    keyword_list
    keywords = ', '.join(keyword_list)
    oracle_text = '\n' + c2['oracle_text'] + '\n' if args.show_oracle_text else ''
    # symbols in oracle text
    if oracle_text:
        for key in oracle_symbol_map:
            oracle_text = oracle_text.replace(key, oracle_symbol_map[key])
    
    # extra line break between types if ordering by type_line
    extraLineBreak = (('\n' if index > 0 and c2['type_line'].split('—')[0].strip() != cards[next_index]['type_line'].split('—')[0].strip() else '') if args.order_by == 'type_line' else '')
    
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
            if not word.lower() in cards[card_index]['type_line'].lower() and not word.lower() in cards[card_index]['oracle_text'].lower():
                hasFilteredWords = False
    
    # create the would-be line of console output
    card_line = c1 + rarity + cardCodeCol + '  ' + nameCol + '  ' + typeLineCol + '  ' + cmcCol + '  ' + RESET + c2['manaDisplay'] + keywords + oracle_text + extraLineBreak + '\n'

    card_index += 1
    
    # show card unless it does not fit filter criteria
    if not hasFilteredColors or not hasFilteredWords: 
        return c1
    
    rendered_cards.append(card)
    card_lines.append(card_line)
    return card_line

card_list_str = functools.reduce(reduce, cards, '')

# Card count (top)
print('\n' + str(len(cards)) + ' cards\n-------')

# Card list
print(card_list_str, end='')

# Mana curve
print('-------\nMana curve')
# 1 - 9
for i in range(0, 10):
    cards_in_row = [c for c in rendered_cards if c['cmc'] == i and not re.fullmatch('.*?land.*?', c['type_line'].lower())]
    mana_count = len(cards_in_row)
    colorless_mana_count    = len([c for c in cards_in_row if    not c['color_identity']])
    white_mana_count        = len([c for c in cards_in_row if 'W' in c['color_identity']])
    blue_mana_count         = len([c for c in cards_in_row if 'U' in c['color_identity']])
    black_mana_count        = len([c for c in cards_in_row if 'B' in c['color_identity']])
    red_mana_count          = len([c for c in cards_in_row if 'R' in c['color_identity']])
    green_mana_count        = len([c for c in cards_in_row if 'G' in c['color_identity']])
    # get the cards with cmc == i AND NOT land
    # print '▇' that many times
    # print(str(i) + ' ' + INVERT + (str(mana_count) if mana_count else '') + (' ' * (round(mana_count) - len(str(round(mana_count))))) + RESET + (' ' * (20 - round(mana_count))) + '...')
    line_str = str(i) + ' ' 
    line_str += '▇' * (round(mana_count)) + RESET + ' ' * (30 - round(mana_count))
    line_str += str(i) + ' '
    line_str += WHITE + ('▇' * (round(white_mana_count)))
    line_str += BLUE + ('▇' * (round(blue_mana_count)))
    line_str += BLACK + ('▇' * (round(black_mana_count)))
    line_str += RED + ('▇' * (round(red_mana_count)))
    line_str += GREEN + ('▇' * (round(green_mana_count)))
    line_str += RESET + ('▇' * (round(colorless_mana_count))) + RESET + (' ' * (30 - round(white_mana_count + blue_mana_count + black_mana_count + red_mana_count + green_mana_count)))
    print(line_str)
# +
cards_in_row = [c for c in rendered_cards if c['cmc'] >= 10 and not re.fullmatch('.*?land.*?', c['type_line'].lower())]
mana_count = len(cards_in_row)
colorless_mana_count    = len([c for c in cards_in_row if    not c['color_identity']])
white_mana_count        = len([c for c in cards_in_row if 'W' in c['color_identity']])
blue_mana_count         = len([c for c in cards_in_row if 'U' in c['color_identity']])
black_mana_count        = len([c for c in cards_in_row if 'B' in c['color_identity']])
red_mana_count          = len([c for c in cards_in_row if 'R' in c['color_identity']])
green_mana_count        = len([c for c in cards_in_row if 'G' in c['color_identity']])
# get the cards with cmc == i AND NOT land
# print '▇' that many times
line_str = '+ ' 
line_str += '▇' * (round(mana_count)) + RESET + ' ' * (30 - round(mana_count))
line_str += '+ '
line_str += WHITE + ('▇' * (round(white_mana_count)))
line_str += BLUE + ('▇' * (round(blue_mana_count)))
line_str += BLACK + ('▇' * (round(black_mana_count)))
line_str += RED + ('▇' * (round(red_mana_count)))
line_str += GREEN + ('▇' * (round(green_mana_count)))
line_str += RESET + ('▇' * (round(colorless_mana_count))) + RESET + (' ' * (30 - round(white_mana_count + blue_mana_count + black_mana_count + red_mana_count + green_mana_count)))
print(line_str)

print('-------\nExample hands\n')
# Example hands
for i in range(3):
    # shuffle
    random.shuffle(rendered_cards)
    # draw 7
    hand = rendered_cards[:7]
    # print(', '.join(hand))
    for card in hand:
        print(card['name'] + ' ' * (32 - len(card['name'])) + ' ' + functools.reduce(lambda c1, c2: c1 + str(oracle_symbol_map.get(c2)), re.findall('{[^{}]+}', card['mana_cost']), '' ) )
    print()
    

# Card count (bottom)
print('-------\n' + str(len(cards)) + ' cards')

if not len(notFound) == 0:
    print('File not modifed. Unknown identifiers: ' + str(functools.reduce(lambda i1, i2: i1 + (', ' if len(i1) > 0 else '') + '\'' + i2['set'] + '/' + i2['collector_number'] + '\'', notFound, '')))

# Elapsed time
elapsed_time = round(time.time() - start_time)
print('\n' + str(elapsed_time) + ' seconds')
