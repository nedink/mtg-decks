def read_cards(filename):
    """Reads the card identifiers from the input file

    Parameters:
        args (object): parsed arguments

    Returns:
        cards: list of cards in json format
    """
    # get file name
    # filename = args.filename

    # check file exists
    if not os.path.exists(filename):
        print('file \'' + filename + '\' does not exist.')
        exit(1)

    # open file
    fo = open(filename, 'r')
    lines = fo.read().splitlines()

    # for each line...
    identifiers = []
    cards = []
    not_found = []
    # loading_message('Looking up cards')
    for index, line in enumerate(lines):
        # if correct format...
        if re.match('[a-zA-Z0-9]+/[0-9]+', line):
            split = line.split('/')
            # create identifier
            if len(split) == 2 and len(split[0]) > 0 and len(split[1]) > 0:
                identifiers.append({
                    'set': split[0].lower(),
                    'collector_number': str(split[1]).lstrip('0')
                })
        # request cards from scryfall
        if len(identifiers) == 75 or index == len(lines) - 1:
            loading_message('Looking up cards ' + '[' + '=' * int(78 * index / len(lines)) + '-' * int(78 - 78 * index / len(lines)) + ']')
            time.sleep(0.1) # sleep 0.1s
            response = requests.post(collection_url, json={'identifiers': identifiers}, timeout=5)
            if not response.ok:
                print(response.json()['details'])
                exit(1)
            cards += response.json()['data']
            not_found = response.json()['not_found']
            identifiers.clear()
    fo.close()
    return cards