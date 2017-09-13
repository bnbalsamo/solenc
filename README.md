# solenc

v1.0.0

[![Build Status](https://travis-ci.org/bnbalsamo/solenc.svg?branch=master)](https://travis-ci.org/bnbalsamo/solenc) [![Coverage Status](https://coveralls.io/repos/github/bnbalsamo/solenc/badge.svg?branch=master)](https://coveralls.io/github/bnbalsamo/solenc?branch=master)

An implementation of [Bruce Schneier's Solitaire encryption algorithm](https://www.schneier.com/academic/solitaire/). 


# Usage Example
```
$ solenc encrypt -d "$(solenc generate)" -k CRYPTONOMICON solitaire
KIRAK SFJAN
```

```
$ solenc decrypt -d "$(solenc generate)" -k CRYPTONOMICON "KIRAK SFJAN"
SOLIT AIREX
```

# Syntax
```
$ solenc --help
usage: solenc [-h] [-v VERBOSITY] {encrypt,decrypt,generate,add,subtract} ...

positional arguments:
  {encrypt,decrypt,generate,add,subtract}

optional arguments:
  -h, --help            show this help message and exit
  -v VERBOSITY, --verbosity VERBOSITY
                        The verbosity for the program to operate at
```

```
$ solenc encrypt --help
usage: solenc encrypt [-h] -d DECK [-k KEY] message

positional arguments:
  message               The plaintext to encrypt

optional arguments:
  -h, --help            show this help message and exit
  -d DECK, --deck DECK  A deck serialization, or filepath for a file
                        containing one.
  -k KEY, --key KEY     A key to apply to the initial state of the deck
```

```
$ solenc decrypt --help
usage: solenc decrypt [-h] -d DECK [-k KEY] message

positional arguments:
  message               The ciphertext to decrypt

optional arguments:
  -h, --help            show this help message and exit
  -d DECK, --deck DECK  A deck serialization, or filepath for a file
                        containing one.
  -k KEY, --key KEY     A key to apply to the initial state of the deck
```

```
$ solenc generate --help
usage: solenc generate [-h] [-d DECK] [-k KEY] [--shuffle]

optional arguments:
  -h, --help            show this help message and exit
  -d DECK, --deck DECK  An initial deck state to operate with. If omitted a
                        bridge order deck with both Jokers at the end will be
                        used.
  -k KEY, --key KEY     A key to apply to to the deck.
  --shuffle             If present the deck is shuffled. You probably only
                        want this if the other two options are omitted in
                        order to produce a random deck.
```

```
$ solenc add --help
usage: solenc add [-h] n m

positional arguments:
  n           The first term
  m           The second term

optional arguments:
  -h, --help  show this help message and exit
```

```
$ solenc subtract --help
usage: solenc subtract [-h] n m

positional arguments:
  n           The first term
  m           The second term

optional arguments:
  -h, --help  show this help message and exit
```

# Author
Brian Balsamo <brian@brianbalsamo.com>
