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

GO_BACK_1000 = '\033[1000D'
ERASE_TO_END = '\033[K'
GO_UP_1 = '\033[1A'

def color256(index):
    return '\033[38;5;' + index

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

rarity_map = {
    'common': '',
    'uncommon': SILVER,
    'rare': GOLD,
    'mythic': ORANGE
}

loading_spinner_index = 0
loading_spinner = [
    '/', '-', '\\', '|'
]