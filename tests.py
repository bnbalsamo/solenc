import unittest
from solenc import Deck, format_str
from tempfile import NamedTemporaryFile
from random import randint, choice
import string


class Tests(unittest.TestCase):
    def test_vectors(self):
        vectors = [
            {
                'Plaintext':  'AAAAAAAAAAAAAAA',
                'Key': None,
                'Output': [4, 49, 10, 53, 24, 8, 51, 44, 6, 4, 33, 20, 39, 19, 34, 42],
                'Ciphertext': 'EXKYI ZSGEH UNTIQ'
            },
            {
                'Plaintext': 'AAAAAAAAAAAAAAA',
                'Key': 'f',
                'Output': [49, 24, 8, 46, 16, 1, 12, 33, 10, 10, 9, 27, 4, 32, 24],
                'Ciphertext': 'XYIUQ BMHKK JBEGY'
            },
            {
                'Plaintext': 'AAAAAAAAAAAAAAA',
                'Key': 'fo',
                'Output':  [19, 46, 9, 24, 12, 1, 4, 43, 11, 32, 23, 39, 29, 34, 22],
                'Ciphertext': 'TUJYM BERLG XNDIW'
            },
            {
                'Plaintext': 'AAAAAAAAAAAAAAA',
                'Key': 'foo',
                'Output': [8, 19, 7, 25, 20, 53, 9, 8, 22, 32, 43, 5, 26, 17, 53, 38, 48],
                'Ciphertext': 'ITHZU JIWGR FARMW'
            },
            {
                'Plaintext': 'AAAAAAAAAAAAAAA',
                'Key':  'a',
                'Output':  [49, 14, 3, 26, 11, 32, 18, 2, 46, 37, 34, 42, 13, 18, 28],
                'Ciphertext': 'XODAL GSCUL IQNSC'
            },
            {
                'Plaintext': 'AAAAAAAAAAAAAAA',
                'Key': 'aa',
                'Output':  [14, 7, 32, 22, 38, 23, 23, 2, 26, 8, 12, 2, 34, 16, 15],
                'Ciphertext':  'OHGWM XXCAI MCIQP'
            },
            {
                'Plaintext': 'AAAAAAAAAAAAAAA',
                'Key': 'aaa',
                'Output':  [3, 28, 18, 42, 24, 33, 1, 16, 51, 53, 39, 6, 29, 43, 46, 45],
                'Ciphertext': 'DCSQY HBQZN GDRUT'
            },
            {
                'Plaintext': 'AAAAAAAAAAAAAAA',
                'Key': 'b',
                'Output':  [49, 16, 4, 30, 12, 40, 8, 19, 37, 25, 47, 29, 18, 16, 18],
                'Ciphertext': 'XQEEM OITLZ VDSQS'
            },
            {
                'Plaintext': 'AAAAAAAAAAAAAAA',
                'Key':  'bc',
                'Output':  [16, 13, 32, 17, 10, 42, 34, 7, 2, 37, 6, 48, 44, 28, 53, 4],
                'Ciphertext': 'QNGRK QIHCL GWSCE'
            },
            {
                'Plaintext': 'AAAAAAAAAAAAAAA',
                'Key':  'bcd',
                'Output': [5, 38, 20, 27, 50, 1, 38, 26, 49, 33, 39, 42, 49, 2, 35],
                'Ciphertext':  'FMUBY BMAXH NQXCJ'
            },
            {
                'Plaintext': 'AAAAAAAAAAAAAAAAAAAAAAAAA',
                'Key': 'cryptonomicon',
                'Ciphertext':  'SUGSR SXSWQ RMXOH IPBFP XARYQ'
            },
            {
                'Plaintext': 'SOLITAIRE',
                'Key':  'cryptonomicon',
                'Ciphertext':  'KIRAK SFJAN'
            }
        ]

        for x in vectors:
            # Three decks, one for encryption, one for generating a raw keystream
            # and the final one for decryption
            d1 = Deck(shuffle=False)
            d2 = Deck(shuffle=False)
            d3 = Deck(shuffle=False)
            if x['Key']:
                d1.key(x['Key'])
                d2.key(x['Key'])
                d3.key(x['Key'])
            # Test ciphertext comes out right
            self.assertEqual(d1.encrypt(format_str(x['Plaintext'])), x['Ciphertext'])
            # Test keystream comes out right, if it's provided
            # My implementation skip 53s in the output,
            # so lets sort those out of the provided output
            if x.get('Output'):
                comp_keystream = [i for i in x['Output'] if i != 53]
                keystream = []
                while len(keystream) < len(comp_keystream):
                    kv = d2.gen_keystream(1)[0]
                    keystream.append(kv)
                self.assertEqual(keystream, comp_keystream)
            self.assertEqual(d3.decrypt(x['Ciphertext']), format_str(x['Plaintext']))

    def test_nonascii_to_x_and_uppercase(self):
        d1 = Deck(shuffle=False)
        d2 = Deck(shuffle=False)
        self.assertEqual(d1.encrypt(format_str("TeST! WItH'")),
                         d2.encrypt(format_str("TESTX WITHX")))

    def test_x_padding(self):
        d1 = Deck(shuffle=False)
        d2 = Deck(shuffle=False)
        self.assertEqual(d1.encrypt(format_str("test")),
                         d2.encrypt(format_str("TESTX")))

    def test_json_serialization(self):
        target_file = NamedTemporaryFile()
        d1 = Deck()
        d1.to_json_file(target_file.name)
        d2 = Deck.from_json_file(target_file.name)
        self.assertEqual(d1, d2)

    def test_newline_delimited_serialization(self):
        target_file = NamedTemporaryFile()
        d1 = Deck()
        d1.to_newline_delimited_file(target_file.name)
        d2 = Deck.from_newline_delimited_file(target_file.name)
        self.assertEqual(d1, d2)

    def test_random_inputs(self):
        for _ in range(100):
            rand_str = ''.join(choice(string.ascii_letters) for _ in range(randint(1, 100)))
            formatted_str = format_str(rand_str)
            d1 = Deck(shuffle=False)
            d2 = Deck.from_json_str(d1.to_json_str())
            encrypted = d1.encrypt(formatted_str)
            self.assertEqual(
                d2.decrypt(encrypted),
                formatted_str
            )


if __name__ == "__main__":
    unittest.main()
