# MTG Collection Visualizer (WIP)

![screenshot](./screenshot.png)

> Requires [Python](https://www.python.org/downloads/). 
>
> Please note that this project is a work in progress. The scripts are not coded optimally, and for large collections may take several minutes to execute. (In the future, I intend to add a progress indicator in addition to execution time improvements!)

## Cromebook

1. At the bottom right, select the time.
2. Select __Settings__.
3. Under "Linux (Beta)," select __Turn On__.
4. Follow the steps on the screen.
5. A terminal window opens. Follow Linux instructions below.

## Linux/macOS

1. Check for updates.

```
sudo apt-get update && sudo apt-get dist-upgrade
```

2. Install `curl`.

```
sudo apt install curl
```

3. Get the `examine.py` script.

```
curl https://raw.githubusercontent.com/nedink/mtg-decks/master/examine.py >> examine.py
```

4. Allow script execution.

```
chmod +x examine.py
```

## Create a Collection File

Collection files have one card per line, in the following format:

```
[SET CODE]/[COLLECTOR NUMBER]
```

Example: 

```
znr/138
```

> The above card code represends the card [Expedition Champion](https://scryfall.com/card/znr/138/expedition-champion?utm_source=api).

## Run the Script

```
python3 examine.py filename [-h] [-o ORDERBY] [-c COLORS] [-w WORDS] [-t] [-M]
```

### Required Arguments

`filename` 

The name of your collection file

Example:

```
python3 examine.py my_collection.txt
```

### Optional flags

`-h` (or pass no arguments)

View usage

`-c` `--color`

Filter by color identity (union operation is performed for multiple)

- `W` white
- `U` blue
- `B` black
- `R` red
- `G` green

Example: 

```
python3 examine.py my_collection.txt -c W -c U
```

`-w` `--word`

Show only cards which contain some text (intersection operation is performed for multiple)

Example:

```
python3 examine.py my_collection.txt -w pirate -w human
```

> Values for color and word filtering are case-insensitive.

`-o`, `--order-by` 

Order the output by a card attribute

- `name` the name of the card
- `cmc` the converted mana cost
- `type_line` the type line
- `power` the card's power
- `toughness` the card's toughness

> The values for `power` and `toughness` are cast to an integer. If that fails, they are interpreted as `0`.

Example: order by card name

```
python3 examine.py my_collection.txt -o name
```

`-t` `--oracle-text` 

Display the oracle text for each card

Example:

```
python3 my_collection.txt -t
```

> This flag only affects whether or not the oracle text is printed to the console. The absence of this flag does not affect ordering or filtering (`-w`, `--word` will still inspect each card's oracle text).

`-M` `--modify` 

Reorder entries in the collection file (the operation may fail if there are malformed entries in the file)

> WARNING: THIS WILL CAUSE THE SCRIPT TO WRITE TO YOUR COLLECTION FILE. It is best practice to make a backup of the file before using this feature.

---

If you find a bug or have ideas for improvement, please open an issue or send mail to nedink@gmail.com