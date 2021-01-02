scryfall_url = 'https://api.scryfall.com/'

collection_url = scryfall_url + 'cards/collection'
word_bank_url = scryfall_url + 'catalog/word-bank'
# common_word_url = 'https://gist.githubusercontent.com/nedink/629124636fc4a135b04812041c00c033/raw/c8de465c3db6a9f35affe968845b5fb9606970d1/common-mtg-words.txt'
keyword_actions_url = scryfall_url + 'catalog/keyword-actions'
keyword_abilities_url = scryfall_url + 'catalog/keyword-abilities'

def get_word_bank():
    """Get the word bank from scryfall and remove common words

    Parameters:

    Returns:
        word_bank (object): the word bank
    """
    loading_message('Looking up keywords...')
    # request word bank from scryfall
    time.sleep(0.1)  # sleep 0.1s
    response = requests.get(word_bank_url, timeout=5)
    if not response.ok:
        print(response.json()['details'])
        exit(1)
    word_bank = response.json()['data']
    # get common words
    with open('common-words-blacklist.txt') as common_words_file:
        common_words = common_words_file.read().splitlines()
        # TODO - remove comment :: common_words = requests.get(common_word_url, timeout=5).text.splitlines()
        # remove common words and special characters from word_bank (better fix should be implemented in future)
        word_bank = [word for word in word_bank if re.fullmatch('[a-zA-Z-]+', word) and not word in common_words]
    reutrn word_bank