def set_power_and_toughness (cards):
    """Sets power and toughness"""
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
    return cards

def sortvalfun(card, order_by):
    """Provide a value to sort by"""
    retval = 0;
    if not order_by:
        retval = 0
    elif not order_by in card:
        retval = 0
    elif isinstance(card[order_by], int) or isinstance(card[order_by], float):
        retval = card[order_by]
    elif isinstance(card[order_by], str):
        retval = card[order_by].lower()
    elif isinstance(card[order_by], list):
        retval = len(card[order_by])
    return retval


def trim_and_mana(cards):
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
            card['manaDisplay'] = functools.reduce(
                lambda s1, s2: s1 + str(color_map.get(s2)) + str(mana_graph_map.get(s2)) + RESET, matches, '')
        else:
            card['manaDisplay'] = ''
        card['manaDisplay'] += ' ' * int(16 - card['cmc'])
    return(cards)