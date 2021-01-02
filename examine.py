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
from view.output import * # from this repo; use variables without qualification
from model.scryfall import * # this repo
from model.process_cards import *
from view.input import *

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


def prep_ui():
    sys.stdout.write('\n')
    sys.stdout.flush()

# timer
start_time = time.time()
cards = read_cards(args.filename)

if args.show_keywords:
    word_bank = get_word_bank()

# pre-sort card processor
cards = set_power_and_toughness(cards)

# sort cards (--order-by)
cards = sorted(cards, key=lambda card: sortvalfun(card, args.order_by))

# cards = sorted(cards, key=lambda card: 0 if not args.order_by
    # else 0 if not args.order_by in card
    #     else card[args.order_by] if isinstance(card[args.order_by], int) or isinstance(card[args.order_by], float)
    #         else card[args.order_by].lower() if isinstance(card[args.order_by], str)
    #             else len(card[args.order_by]) if isinstance(card[args.order_by], list) else 0)

# modify file (--modify-file)
if args.modify and len(not_found) == 0:
    write_deck_string(cards, args.filename)

# trim word, figure out mana cost
cards = trim_and_mana(cards)
    
# Console display - cards 
rendered_cards = []
card_lines = []
card_index = next_index = 0
processing_iter_time = time.time()
def reduce(c1, c2):
    global card_lines, card_index, next_index, word_bank, loading_spinner, loading_spinner_index, processing_iter_time
    card = cards[card_index]
    next_index += 1
    next_index = min(next_index, len(cards) - 1)

    # check for filtered colors (card identity must include ANY)
    hasFilteredColors = not args.colors
    if args.colors and card['color_identity']:
        for color in args.colors:
            if color.upper() in card['color_identity']:
                hasFilteredColors = True
    
    # check for filtered words (card text must include ALL)
    hasFilteredWords = True
    if args.words:
        for word in args.words:
            if not word.lower() in card['type_line'].lower() and (not word.lower() in card['oracle_text'].lower() if 'oracle_text' in card else False):
                hasFilteredWords = False

    # do not continue unless card matches filter criteria
    if not hasFilteredColors or not hasFilteredWords: 
        card_index += 1
        return c1

    cardCodeCol = (c2['set'] + '/' + c2['collector_number']).ljust(8)
    nameCol = c2['name'].ljust(32, '─' if index % 2 == 0 else '─')
    typeLineCol = c2['type_line'].ljust(32, '─' if index % 2 == 0 else '─')
    cmcCol = (str(int(c2['cmc'])) if c2['cmc'] % 1 == 0 else str(c2['cmc'])).ljust(3)
    rarity = rarity_map.get(c2['rarity'])
    # TODO - this bad boy needs to go faster
    keywords = ', '.join([word for index, word in enumerate(word_bank) if re.search('\\W' + word + '\\W', card['type_line'].lower() + ' ' + card['oracle_text'].lower() if 'oracle_text' in card else '')] if args.show_keywords else [])
    oracle_text = '\n' + c2['oracle_text'] + '\n' if args.show_oracle_text and 'oracle_text' in c2 else ''
    # symbols in oracle text
    if oracle_text:
        for key in oracle_symbol_map:
            oracle_text = oracle_text.replace(key, oracle_symbol_map[key])
    
    # extra line break between types if ordering by type_line
    extraLineBreak = (('\n' if index > 0 and c2['type_line'].split('—')[0].strip() != cards[next_index]['type_line'].split('—')[0].strip() else '') if args.order_by == 'type_line' else '')

    # create the would-be line of console output
    card_line = c1 + rarity + cardCodeCol + '  ' + nameCol + '  ' + typeLineCol + '  ' + cmcCol + '  ' + RESET + c2['manaDisplay'] + keywords + oracle_text + extraLineBreak + '\n'

    card_index += 1

    rendered_cards.append(card)
    card_lines.append(card_line)
    loading_message('Processing ' + '▇' * round((card_index + 1) / len(cards) * 80) + '‧' * max(80 - round((card_index + 1) / len(cards) * 80), 0) + ' ' + str(round(time.time() - processing_iter_time, 2)))
    processing_iter_time = time.time()
    return card_line

card_list_str = functools.reduce(reduce, cards, '')

sys.stdout.write(GO_UP_1 + GO_BACK_1000 + ERASE_TO_END)

print()

# Card count (top)
print('%i/%i cards' % (len(rendered_cards), len(cards)))
print('-' * 100, end='')

# Card list
print(card_list_str, end='')

# Mana curve
print('-' * 100 + '\nMana curve')
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
    line_str += '▇' * (round(mana_count)) + RESET + ' ' * (32 - round(mana_count))
    line_str += ' ' + str(i) + ' '
    line_str += WHITE + ('▇' * (round(white_mana_count)))
    line_str += BLUE + ('▇' * (round(blue_mana_count)))
    line_str += BLACK + ('▇' * (round(black_mana_count)))
    line_str += RED + ('▇' * (round(red_mana_count)))
    line_str += GREEN + ('▇' * (round(green_mana_count)))
    line_str += RESET + ('▇' * (round(colorless_mana_count))) + RESET + ' ' * (32 - round(white_mana_count + blue_mana_count + black_mana_count + red_mana_count + green_mana_count))
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
line_str += '▇' * (round(mana_count)) + RESET + ' ' * (32 - round(mana_count))
line_str += ' + '
line_str += WHITE + ('▇' * (round(white_mana_count)))
line_str += BLUE + ('▇' * (round(blue_mana_count)))
line_str += BLACK + ('▇' * (round(black_mana_count)))
line_str += RED + ('▇' * (round(red_mana_count)))
line_str += GREEN + ('▇' * (round(green_mana_count)))
line_str += RESET + ('▇' * (round(colorless_mana_count))) + RESET + (' ' * (32 - round(white_mana_count + blue_mana_count + black_mana_count + red_mana_count + green_mana_count)))
print(line_str)

print('-' * 100 + '\nExample hands\n')
# Example hands
for i in range(3):
    # shuffle
    random.shuffle(rendered_cards)
    # draw 7
    hand = rendered_cards[:7]
    for card in hand:
        card_line = rarity_map.get(card['rarity']) + card['name'] + ' ' * (32 - len(card['name']))
        if re.fullmatch('.*?land.*?', card['type_line'].lower()):
            card_line += ' Land ' + (functools.reduce(lambda c1, c2: c1 + color_map.get(c2) + '▇', card['color_identity'], '') if card['color_identity'] else '') + RESET
        else:
            card_line += RESET + ' ' + functools.reduce(lambda c1, c2: c1 + str(oracle_symbol_map.get(c2)), re.findall('{[^{}]+}', card['mana_cost']), '' )
        print(card_line)
    print()
    

# Card count (bottom)
print('-' * 100)
print('%i/%i cards' % (len(rendered_cards), len(cards)))

if not len(not_found) == 0:
    print('File not modifed. Unknown identifiers: ' + str(functools.reduce(lambda i1, i2: i1 + (', ' if len(i1) > 0 else '') + '\'' + i2['set'] + '/' + i2['collector_number'] + '\'', not_found, '')))

# Elapsed time
elapsed_time = round(time.time() - start_time)
print('\n' + str(elapsed_time) + ' seconds')
