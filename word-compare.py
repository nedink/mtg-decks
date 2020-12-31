#!/usr/bin/env python3

import requests
import io

common_word_url = 'https://gist.githubusercontent.com/nedink/a0e9da7807ef1d06c8318fcffe627dc4/raw/98d35708fa344717d8eee15d11987de6c8e26d7d/1-1000.txt'
word_bank_url = 'https://api.scryfall.com/catalog/word-bank'

common_words = requests.get(common_word_url).text.splitlines()

word_bank = requests.get(word_bank_url).json()['data']

result = '\n'.join([word for word in word_bank if word in common_words])

print(result)

