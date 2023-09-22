import os
import pandas as pd
import pathlib 
import json

exec_dir = os.path.dirname(os.path.realpath(__file__))

words_filepath = pathlib.Path(exec_dir).parent / 'words' / '2018' / 'en_50k.txt' 
letters_to_prefixes_suffixes_filepath = \
    pathlib.Path(exec_dir) / '_3x10_prefix_suffix.json'

shorthands_filepath = pathlib.Path(exec_dir).parent / 'shorthands.json'

MIN_WORD_LEN = 7
MIN_FREQ = 1000

WORD_KEY = 'word'
PREFIXES_KEY = 'prefixes'
ROOT_WORD_KEY = 'root_word'
SUFFIXES_KEY = 'suffixes'
SHORTHAND_KEY = 'shorthand'

VOWELS = ['a', 'e', 'i', 'o', 'u', 'y']
SH_DELIM = '|'


# closure to get the gen_algo_fn
def get_gen_algo_fn():

    with open(letters_to_prefixes_suffixes_filepath, 'r') as f:
        letters = json.load(f)

    def gen_algo_fn(word):
        prefixes = []
        prefixes_shorthand = []
        suffixes = []
        suffixes_shorthand = []
        root_word = word 

        # search for prefixes
        for i in range(len(word)):
            if word[i] in letters:
                for prefix in letters[word[i]]["prefixes"]:
                    if word.startswith(prefix):
                        prefixes.append(prefix)
                        prefixes_shorthand.append(word[i]) # append letter
                        root_word = root_word[len(prefix):]
                        break

        # search for suffixes
        for i in range(len(word)-1, -1, -1):
            if word[i] in letters:
                for suffix in letters[word[i]]["suffixes"]:
                    if word.endswith(suffix):
                        suffixes.append(suffix)
                        suffixes_shorthand.append(word[i]) # append letter
                        root_word = root_word[:-len(suffix)]
                        break

        # remove vowels from root word
        root_word_with_vowels = root_word
        root_word = ''.join([c for c in root_word if c not in VOWELS])

        # take only the first 3 letters of the root word
        shorthand = ''.join(prefixes_shorthand) + SH_DELIM + \
                                  root_word[:3] + SH_DELIM + \
                    ''.join(suffixes_shorthand)

        return  { 
            word : 
            {  
                SHORTHAND_KEY: shorthand, 
                PREFIXES_KEY: prefixes,
                ROOT_WORD_KEY: root_word_with_vowels,
                SUFFIXES_KEY: suffixes,
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

    for index, row in df.iterrows():
        word, freq, length = row['word'], int(row['freq']), row['length']

        if type(word) != str:
            print(f"\tSkipping {word} with type {type(word)}")
            continue

        if length < MIN_WORD_LEN or freq < MIN_FREQ:
            print(f"Skipping {word} with length {length} and freq {freq}")
            continue
        
        sh_dict = gen_algo_fn(word)
        shorthand = sh_dict[word][SHORTHAND_KEY]

        if shorthand not in shorthands_dict:
            shorthands_dict[shorthand] = []
        
        shorthands_dict[shorthand].append(sh_dict)
        
    with open(shorthands_filepath, 'w') as f:
        json.dump(shorthands_dict, f, indent=4)


if __name__ == '__main__':
    main()

