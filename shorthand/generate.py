import os
import pandas as pd
import pathlib 
import json
from enum import Enum

class WORDLIST(Enum):
    FULL = 0
    TOP_FIFTY_THOUSAND = 1

MIN_WORD_LEN = 7
MIN_FREQ = 100 # accomodated is freq 160
MIN_ROOT_WORD_LEN = 3 # idk 
LONGEST_PREFIX_LEN = 6 # contra
LONGEST_SUFFIX_LEN = 7 # ability

VOWELS = ['a', 'e', 'i', 'o', 'u', 'y']
ALLOWED_SHORTHAND_CHARACTERS = "abcdefghijklmnopqrstuvwxyz,.';"
SH_DELIM = '|'

# TODO: make this a command line arg

# change this to en_full_filename if you want to use the full word list or the top 50k
WORDLIST_TO_USE = WORDLIST.FULL
#WORDLIST_TO_USE = WORDLIST.TOP_FIFTY_THOUSAND

exec_dir = os.path.dirname(os.path.realpath(__file__))

letters_to_prefixes_suffixes_filepath = pathlib.Path(exec_dir) / '_3x10_prefix_suffix.json'
en_full_filename = 'en_full.txt'
en_50k_filename = 'en_50k.txt'
shorthands_en_full_filename = 'shorthands_en_full.json'
shorthands_en_50k_filename ='shorthands_en_50k.json'

words_filepath = pathlib.Path(exec_dir).parent / 'words' / '2018'
shorthands_filepath = pathlib.Path(exec_dir)
if WORDLIST_TO_USE == WORDLIST.FULL:
    words_filepath = words_filepath / en_full_filename
    shorthands_filepath = shorthands_filepath / shorthands_en_full_filename 
elif WORDLIST_TO_USE == WORDLIST.TOP_FIFTY_THOUSAND:
    words_filepath = words_filepath / en_50k_filename
    shorthands_filepath = shorthands_filepath / shorthands_en_50k_filename 
else:
    raise Exception("Invalid wordlist to use")

WORD_KEY = 'word'
PREFIXES_KEY = 'prefixes'
ROOT_WORD_KEY = 'root_word'
SUFFIXES_KEY = 'suffixes'
SHORTHAND_KEY = 'shorthand'


# closure to get the gen_algo_fn
def get_gen_algo_fn():

    with open(letters_to_prefixes_suffixes_filepath, 'r') as f:
        letter_to_presufs = json.load(f)

    def gen_algo_fn(word):
        found_prefixes = []
        found_prefixes_shorthand = []
        found_suffixes = []
        found_suffixes_shorthand = []
        original_word = word 

        # search for prefixes
        no_more_prefixes = False
        while not no_more_prefixes and len(word) >= MIN_ROOT_WORD_LEN:
            no_more_prefixes = True # assume no more prefixes

            # find all possible prefixes and sort them by length descending
            possible_prefix_letters = set(word[:LONGEST_PREFIX_LEN])
            possible_prefixes = [] # list of prefixes to search for in word
            prefix_to_letter = {} # backreference to letter

            for letter in possible_prefix_letters:
                letter_prefixes = letter_to_presufs[letter][PREFIXES_KEY]

                if letter_prefixes is None:
                    continue

                for prefix in letter_prefixes:
                    prefix_to_letter[prefix] = letter
                    possible_prefixes.append(prefix)

            possible_prefixes.sort(key=lambda x: len(x), reverse=True) # sort by length descending

            for prefix in possible_prefixes:
                if word.startswith(prefix): # found prefix
                    found_prefixes.append(prefix)
                    found_prefixes_shorthand.append(prefix_to_letter[prefix]) # append letter
                    word = word[len(prefix):] # remove prefix from word
                    no_more_prefixes = False
                    break


        # search for suffixes
        no_more_suffixes = False
        while not no_more_suffixes and len(word) >= MIN_ROOT_WORD_LEN:
            no_more_suffixes = True # assume no more suffixes

            # find all possible suffixes and sort them by length descending
            possible_suffix_letters = set(word[-LONGEST_SUFFIX_LEN:])
            possible_suffixes = []
            suffix_to_letter = {}

            for letter in possible_suffix_letters:
                letter_suffixes = letter_to_presufs[letter][SUFFIXES_KEY]

                if letter_suffixes is None:
                    continue

                for suffix in letter_suffixes:
                    suffix_to_letter[suffix] = letter
                    possible_suffixes.append(suffix) # to be reversed later

            possible_suffixes.sort(key=lambda x: len(x), reverse=True) # sort by length descending

            for suffix in possible_suffixes:
                if word.endswith(suffix): # found suffix
                    found_suffixes.append(suffix)
                    found_suffixes_shorthand.append(suffix_to_letter[suffix]) # to be reversed later
                    word = word[:-len(suffix)] # remove suffix from word
                    no_more_suffixes = False
                    break

        # remove vowels from root word and take the first 3 letters
        root_word_with_vowels = word # the remaining word is the root word, assuming the above algo is correct
        root_word_shorthand = ''.join([c for c in root_word_with_vowels if c not in VOWELS])[:3]

        # construct the shorthand
        shorthand = ''.join(found_prefixes_shorthand) + SH_DELIM + \
                                  root_word_shorthand + SH_DELIM + \
                    ''.join(found_suffixes_shorthand[::-1])

        return  { 
            original_word : 
            {  
                SHORTHAND_KEY: shorthand, 
                PREFIXES_KEY: found_prefixes,
                ROOT_WORD_KEY: root_word_with_vowels,
                SUFFIXES_KEY: found_suffixes[::-1],
            }
        }

    return gen_algo_fn


# This script generates a shorthand for the given word.
def main():

    df = pd.read_csv(words_filepath, sep=' ', header=None, names=['word', 'freq'])
    
    # make a new column with the length of the word
    df['length'] = df['word'].str.len()
    df.info()
    
    gen_algo_fn = get_gen_algo_fn()

    shorthands_dict = {}

    number_of_min_freq_skipped = 0
 
    for index, row in df.iterrows():
        word, freq, length = row['word'], int(row['freq']), row['length']

        if type(word) != str:
            print(f"\tSkipping {word} with type {type(word)}")
            continue

        if length < MIN_WORD_LEN or freq < MIN_FREQ:
            print(f"Skipping {word} with length {length} and freq {freq}")
            if freq < MIN_FREQ:
                number_of_min_freq_skipped += 1
            if number_of_min_freq_skipped >= MIN_FREQ:
                print("Stopping because we've skipped 100 words with freq < {MIN_FREQ}")
                break

            continue
        
        if not all(c in ALLOWED_SHORTHAND_CHARACTERS for c in word):
            print(f"\tSkipping {word} with invalid characters")
            continue
        
        number_of_min_freq_skipped = 0

        sh_dict = gen_algo_fn(word)
        shorthand = sh_dict[word][SHORTHAND_KEY]

        if shorthand not in shorthands_dict:
            shorthands_dict[shorthand] = []
        
        shorthands_dict[shorthand].append(sh_dict)
        
    with open(shorthands_filepath, 'w') as f:
        json.dump(shorthands_dict, f, indent=4)


if __name__ == '__main__':
    main()

