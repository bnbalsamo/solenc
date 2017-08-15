from random import shuffle as _shuffle
from random import SystemRandom
import string
from json import dumps, loads
import argparse
import logging
from sys import stdout


# Portions taken from: https://gist.github.com/jesux/0a2d243b3fdcc8827adf


"""
An implementation of Bruce Schneier's Solitaire Encryption Algorithm
(https://www.schneier.com/academic/solitaire/) in python, written with the
aim of making the code easy to use in conjunction with a physical deck
or a physical deck list.
"""


log = logging.getLogger(__name__)


# Strings commonly used to refer to card values within a suite
strs2values = {
    ("Ace", "one", "1"): 1,
    ("Two", "2", "deuce"): 2,
    ("Three", "3"): 3,
    ("Four", "4"): 4,
    ("Five", "5"): 5,
    ("Six", "6"): 6,
    ("Seven", "7"): 7,
    ("Eight", "8"): 8,
    ("Nine", "9"): 9,
    ("Ten", "10"): 10,
    ("Jack", "11"): 11,
    ("Queen", "12"): 12,
    ("King", "13"): 13
}

# The inverse of the above {int: tuple[str]} for convenience
values2strs = {
    strs2values[k]: k for k in strs2values
}


# Suite strings
# Bridge order
suites = [
    "Clubs",
    "Diamonds",
    "Hearts",
    "Spades"
]


# Offsets per suite
# Bridge order, 52 card deck
offsets = {
    "Clubs": 0,
    "Diamonds": 13,
    "Hearts": 13+13,
    "Spades": 13+13+13
}


def to_number(c):
    """
    Convert letter to number: Aa->1, Bb->2, ..., Zz->26.
    Non-letters are treated as X's.
    """
    if c in string.ascii_letters:
        return ord((c.upper())) - 64
    return 24  # 'X'


def to_character(n):
    """
    Convert number to letter: 1->A,  2->B, ..., 26->Z,
    27->A, 28->B, ... ad infitum
    """
    return chr((n-1) % 26+65)


def to_deck_value(c):
    return offsets[c.get_suite()] + c.get_value()


class Card:
    """
    A class for representing a playing card
    """
    def __init__(self, suite, value):
        self._suite = None
        self._value = None

        self.set_suite(suite)
        self.set_value(value)

    @classmethod
    def loads(cls, x):
        value, suite = x.split(" of ")
        return Card(suite, value)

    def __eq__(self, other):
        if self.get_suite() == other.get_suite() and \
                self.get_value() == other.get_value():
            return True
        return False

    def __gt__(self, other):
        if self.get_suite() != other.get_suite():
            if suites.index(self.get_suite()) > suites.index(other.get_suite()):
                return True
        else:
            if self.get_value() > other.get_value():
                return True
        return False

    def __repr__(self):
        return "{} of {}".format(
            values2strs[self.get_value()][0], self.get_suite()
        )

    def set_value(self, value):
        if value in range(1, 14):
            self._value = value
            return
        for str_tuple in strs2values:
            if value.lower() in [x.lower() for x in str_tuple]:
                self._value = strs2values[str_tuple]
                return
        raise ValueError("Not a recognized card value")

    def get_value(self):
        return self._value

    def set_suite(self, suite):
        for x in suites:
            if suite.lower() == x.lower():
                self._suite = x
                return
        raise ValueError("Not a recognized suite")

    def get_suite(self):
        return self._suite

    suite = property(get_suite, set_suite)
    value = property(get_value, set_value)


class Joker(Card):
    """
    Limited subclass of Card for representing Jokers
    """

    _suite = "Joker"

    def __init__(self, value):
        self._value = value

    @classmethod
    def loads(cls, x):
        return Joker(x.split("(")[1][:-1])

    def __gt__(self, other):
        raise ValueError()

    def __repr__(self):
        return "Joker ({})".format(str(self._value))

    def set_suite(self):
        raise NotImplemented

    def set_value(self, value):
        self._value = value


class Deck:
    """
    Container object for cards and algorithm step implementations
    Note this is a stateful container, operations will change the
    card order if appropriate.
    """
    @classmethod
    def from_list(cls, cards_list, shuffle=False):
        cards = []
        for x in cards_list:
            if x.startswith("Joker"):
                cards.append(Joker.loads(x))
            else:
                cards.append(Card.loads(x))
        return Deck(cards=cards, shuffle=shuffle)

    @classmethod
    def from_json_str(cls, json, shuffle=False):
        cards_list = loads(json)
        return cls.from_list(cards_list, shuffle=shuffle)

    @classmethod
    def from_newline_delimited_str(cls, nlstr, shuffle=False):
        cards_list = nlstr.split("\n")
        return cls.from_list(cards_list, shuffle=shuffle)

    @classmethod
    def from_json_file(cls, fp, shuffle=False):
        with open(fp) as f:
            json_str = f.read()
        return cls.from_json_str(json_str, shuffle=shuffle)

    @classmethod
    def from_newline_delimited_file(cls, fp, shuffle=False):
        with open(fp) as f:
            nlstr = f.read()
        # take care of any pesky hanging newlines
        nlstr = nlstr.rstrip("\n")
        return cls.from_newline_delimited_str(nlstr, shuffle=shuffle)

    def __init__(self, shuffle=True, jokers=True, cards=None):
        self._cards = []

        if cards is None:
            for suite in suites:
                for value in range(1, 14):
                    self.add_card(Card(suite, value))
            if jokers:
                self.add_card(Joker("A"))
                self.add_card(Joker("B"))
        else:
            self.set_cards(cards)
        if shuffle:
            self.shuffle()

    def __eq__(self, other):
        return self.cards == other.cards

    def get_cards(self):
        return self._cards

    def set_cards(self, cards):
        for x in cards:
            self.add_card(x)

    def add_card(self, card):
        if not isinstance(card, Card):
            raise TypeError()
        self._cards.append(card)

    def pop_card(self):
        return self._cards.pop()

    def shuffle(self):
        _shuffle(self._cards, random=SystemRandom().random)

    def del_cards(self):
        self._cards = []

    def to_list(self):
        return [str(x) for x in self.get_cards()]

    def to_json_str(self):
        return dumps(self.to_list())

    def to_newline_delimited_str(self):
        return "\n".join(self.to_list())

    def to_json_file(self, fp):
        with open(fp, 'w') as f:
            f.write(self.to_json_str())

    def to_newline_delimited_file(self, fp):
        with open(fp, 'w') as f:
            f.write(self.to_newline_delimited_str())

    def triple_cut(self):
        joker_indices = []
        for i, x in enumerate(self._cards):
            if isinstance(x, Joker):
                joker_indices.append(i)
        self._cards[:] = self._cards[joker_indices[1]+1:] + \
            self._cards[joker_indices[0]:joker_indices[1]+1] + \
            self._cards[0:joker_indices[0]]

    def count_cut(self, cut_at=None):
        if cut_at is None:
            bottom_card = self._cards[-1]
            if isinstance(bottom_card, Joker):
                return
            cut_at = to_deck_value(bottom_card)
        self._cards[:-1] = self._cards[cut_at:-1] + self._cards[:cut_at]

    def move_down_1(self, card):
        # If it's the last card move it to the front
        if self._cards[-1] == card:
                x = self._cards.pop()
                self._cards.insert(0, x)
        n = self._cards.index(card)
        self._cards[n], self._cards[n+1] = self._cards[n+1], self._cards[n]

    def get_keynum(self):
        top_card = self._cards[0]
        if isinstance(top_card, Joker):
            topcard_value = 53
        else:
            topcard_value = to_deck_value(top_card)
        selected_card = self._cards[topcard_value]
        if isinstance(selected_card, Joker):
            raise ValueError("Selected a Joker")
        else:
            selected_card_value = to_deck_value(selected_card)
        return selected_card_value

    def gen_keystream(self, l):
        keystream = []
        a_joker = Joker("A")
        b_joker = Joker("B")
        i = 0
        while i < l:
            self.move_down_1(a_joker)
            self.move_down_1(b_joker)
            self.move_down_1(b_joker)
            self.triple_cut()
            self.count_cut()
            try:
                keynum = self.get_keynum()
            except ValueError:  # It's a Joker, skip this round and repeat
                continue
            keystream.append(keynum)
            i += 1
        return keystream

    def key(self, passphrase):
        a_joker = Joker("A")
        b_joker = Joker("B")
        for char in passphrase:
            char_num = to_number(char)
            self.move_down_1(a_joker)
            self.move_down_1(b_joker)
            self.move_down_1(b_joker)
            self.triple_cut()
            self.count_cut()
            self.count_cut(char_num)

    def encrypt(self, message):
        encrypted_str = ""
        for char in message:
            # Leave spaces intact, it's up to the caller
            # to properly format the string to not leak
            # information via character groupings.
            # See format_str below for an example
            if char == " ":
                encrypted_str = encrypted_str + " "
                continue
            keynum = self.gen_keystream(1)[0]
            cleartext_charnum = to_number(char)
            cipher_num = keynum + cleartext_charnum
            cipher_char = to_character(cipher_num)
            encrypted_str = encrypted_str + cipher_char
        return encrypted_str

    def decrypt(self, message):
        decrypted_str = ""
        for char in message:
            if char == " ":
                decrypted_str = decrypted_str + " "
                continue
            keynum = self.gen_keystream(1)[0]
            ciphertext_charnum = to_number(char)
            cleartext_charnum = ciphertext_charnum - keynum
            cleartext_char = to_character(cleartext_charnum)
            decrypted_str = decrypted_str + cleartext_char
        return decrypted_str

    cards = property(get_cards, set_cards, del_cards)


def lazy_deck_load(some_str):
    """
    Try to load a deck serialization every way possible
    """
    d = None
    for x in (Deck.from_json_str,
              Deck.from_newline_delimited_str,
              Deck.from_json_file,
              Deck.from_newline_delimited_file):
        try:
            d = x(some_str)
        except:
            pass
    if d is None:
        raise ValueError("Unrecognized deck format!")
    return d


def lazy_value_load(some_str):
    """
    Try to load a "value" any way possible

    Values may look like:
      - 1
      - Ace of Clubs
      - a
    """
    v = None
    try:
        c = Card.loads(some_str)
        v = to_deck_value(c)
        return to_number(to_character(v))
    except:
        pass
    try:
        v = int(some_str)
        return to_number(to_character(v))
    except:
        pass
    try:
        if len(some_str) == 1:
            v = to_number(some_str)
            return v
    except:
        pass
    if v is None:
        raise ValueError("Unrecognized value!")
    return v


def format_str(in_str):
    """
    Format an input string for encryption

    - Replace unencryptable characters with X's
    - Translate messages to all upper case letters
    - Group characters into sets of 5, eg:
       "XXXXX XXXXX XXXXX ..."
    - Pad messages to a complete group of 5 with X's, eg:
       "ABC" -- > "ABCXX"
    """
    # Filter/Upper/Remove Spaces
    filtered_str = ""
    for char in in_str:
        if char == " ":
            continue
        if char not in string.ascii_letters + " ":
            filtered_str += "X"
        else:
            filtered_str += char.upper()

    # Pad the str
    while len(filtered_str) % 5 != 0:
        filtered_str += "X"

    # Insert a space every five characters
    final_str = ""
    for i, char in enumerate(filtered_str):
        if (i > 0) and (i % 5 == 0):
            final_str += " "
        final_str += char
    return final_str


def main():
    parser = argparse.ArgumentParser()
    # Global arguments
    parser.add_argument(
        "-v", "--verbosity", default="WARN",
        help="The verbosity for the program to operate at"
    )

    subparsers = parser.add_subparsers(dest='subparser_name')

    # Encrypt subparser
    encrypt_parser = subparsers.add_parser("encrypt")
    encrypt_parser.add_argument(
        "-d", "--deck", required=True,
        help="A deck serialization, or filepath for a file containing one."
    )
    encrypt_parser.add_argument(
        "-k", "--key", default=None,
        help="A key to apply to the initial state of the deck"
    )
    encrypt_parser.add_argument(
        "message",
        help="The plaintext to encrypt"
    )

    # Decrypt subparser
    decrypt_parser = subparsers.add_parser("decrypt")
    decrypt_parser.add_argument(
        "-d", "--deck", required=True,
        help="A deck serialization, or filepath for a file containing one."
    )
    decrypt_parser.add_argument(
        "-k", "--key", default=None,
        help="A key to apply to the initial state of the deck"
    )
    decrypt_parser.add_argument(
        "message",
        help="The ciphertext to decrypt"
    )

    # Generate subparser
    generate_parser = subparsers.add_parser("generate")
    generate_parser.add_argument(
        "-d", "--deck", default=None,
        help="An initial deck state to operate with.\n" +
        "If omitted a bridge order deck with both Jokers \n" +
        "at the end will be used."
    )
    generate_parser.add_argument(
        "-k", "--key", default=None,
        help="A key to apply to to the deck."
    )
    generate_parser.add_argument(
        "--shuffle", action='store_true',
        help="If present the deck is shuffled. \n" +
        "You probably only want this if the other two options \n" +
        "are omitted in order to produce a random deck."
    )

    # Addition subparser
    addition_parser = subparsers.add_parser("add")
    addition_parser.add_argument("n", help="The first term")
    addition_parser.add_argument("m", help="The second term")

    # Subtraction subparser
    subtraction_parser = subparsers.add_parser("subtract")
    subtraction_parser.add_argument("n", help="The first term")
    subtraction_parser.add_argument("m", help="The second term")

    args = parser.parse_args()

    logging.basicConfig(level=args.verbosity)

    # Encryption functionality
    if args.subparser_name == "encrypt":
        d = lazy_deck_load(args.deck)
        log.info(
            "Initial deck state\n" +
            "------------------\n" +
            "{}".format(d.to_newline_delimited_str())
        )
        if args.key:
            d.key(args.key)
            log.info(
                "Keyed deck state\n" +
                "------------------\n" +
                "{}".format(d.to_newline_delimited_str())
            )

        formatted_str = format_str(args.message)
        encrypted_str = d.encrypt(formatted_str)
        stdout.write(encrypted_str + "\n")

    # Decryption functionality
    elif args.subparser_name == "decrypt":
        d = lazy_deck_load(args.deck)
        log.info(
            "Initial deck state\n" +
            "------------------\n" +
            "{}".format(d.to_newline_delimited_str())
        )
        if args.key:
            d.key(args.key)
            log.info(
                "Keyed deck state\n" +
                "------------------\n" +
                "{}".format(d.to_newline_delimited_str())
            )
        stdout.write(d.decrypt(args.message)+"\n")

    # Deck generator/keyer
    elif args.subparser_name == "generate":
        if args.deck is None:
            d = Deck(shuffle=False)
        else:
            d = lazy_deck_load(args.deck)
        if args.key:
            d.key(args.key)
        if args.shuffle:
            d.shuffle()
        deck_list = d.to_newline_delimited_str()
        stdout.write(deck_list+"\n")

    # Addition utility
    elif args.subparser_name == "add":
        n_val = lazy_value_load(args.n)
        m_val = lazy_value_load(args.m)
        stdout.write("{} + {}\n".format(str(n_val), str(m_val)))
        s = n_val + m_val
        stdout.write(to_character(s)+"\n")

    # Subtraction utility
    elif args.subparser_name == "subtract":
        n_val = lazy_value_load(args.n)
        m_val = lazy_value_load(args.m)
        stdout.write("{} - {}\n".format(str(n_val), str(m_val)))
        s = n_val - m_val
        stdout.write(to_character(s)+"\n")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
