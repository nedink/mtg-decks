#!/usr/bin/env python3

import requests
import functools
import argparse
import os.path
import re
import sys
import time
import random
import json

RESET = '\033[0m'

SILVER = '\033[38;5;159m'
GOLD = '\033[38;5;220m'
ORANGE = '\033[38;5;208m'

scryfall_url = 'https://api.scryfall.com/cards/collection'

# set up parser
parser = argparse.ArgumentParser()
parser.add_argument('filename')
parser.add_argument('-s', '--set', dest='set')
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

# get cards from scryfall
identifiers = []
cards = []
notFound = []
# for each line in file...
for index, line in enumerate(lines, start=1):
    # check format
    if re.match('[a-zA-Z0-9]+/[0-9]+', line):
        split = line.split('/')
        if not args.set or split[0] == args.set:
            # create identifier
            if len(split) == 2 and len(split[0]) > 0 and len(split[1]) > 0: 
                identifiers.append({
                    'set': split[0],
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

common = []
uncommon = []
rare_mythic = []

for card in cards:
    if card['rarity'] == 'common':
        common.append(card)
    if card['rarity'] == 'uncommon':
        uncommon.append(card)
    if card['rarity'] == 'rare' or card['rarity'] == 'mythic':
        rare_mythic.append(card)

# shuffle cards
random.shuffle(common)
random.shuffle(uncommon)
random.shuffle(rare_mythic)

# create booster packs
packs = []
while not (len(common) < 10 or len(uncommon) < 3 or len(rare_mythic) < 1):
    pack = {
        'common': common[:10], # 10 common
        'uncommon': uncommon[:3], # 3 uncommon
        'rare_mythic': rare_mythic[:1] # 1 rare/mythic
    }
    common[:10] = []
    uncommon[:3] = []
    rare_mythic[:1] = []
    packs.append(pack)

# stub pack for the remaining cards
remainder = {
    'common': common[:],
    'uncommon': uncommon[:],
    'rare_mythic': rare_mythic[:]
}

# display cards
print(str(len(cards)) + ' cards')
# display packs
print(str(len(packs)) + ' packs\n')
# print((packs))
for pack in packs:
    p_str = ''
    for card in pack['common']:
        p_str += (card['set'] + '/' + card['collector_number']).ljust(9) + card['name'] + RESET + '\n'
    for card in pack['uncommon']:
        p_str += SILVER + (card['set'] + '/' + card['collector_number']).ljust(9) + card['name'] + RESET + '\n'
    for card in pack['rare_mythic']:
        if card['rarity'] == 'rare':
            p_str += GOLD + (card['set'] + '/' + card['collector_number']).ljust(9) + card['name'] + RESET + '\n'
        if card['rarity'] == 'mythic':
            p_str += ORANGE + (card['set'] + '/' + card['collector_number']).ljust(9) + card['name'] + RESET + '\n'
    print(p_str)

print('Remainder:')
p_str = ''
for card in remainder['common']:
    p_str += (card['set'] + '/' + card['collector_number']).ljust(9) + card['name'] + RESET + '\n'
for card in remainder['uncommon']:
    p_str += SILVER + (card['set'] + '/' + card['collector_number']).ljust(9) + card['name'] + RESET + '\n'
for card in remainder['rare_mythic']:
    if card['rarity'] == 'rare':
        p_str += GOLD + (card['set'] + '/' + card['collector_number']).ljust(9) + card['name'] + RESET + '\n'
    if card['rarity'] == 'mythic':
        p_str += ORANGE + (card['set'] + '/' + card['collector_number']).ljust(9) + card['name'] + RESET + '\n'
print(p_str)
