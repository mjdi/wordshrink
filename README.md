# wordshrink

Windows utility for generating rule/hash-based p(refix)|r(oo)t|(suffi)x shorthand accessed by holding Space

## Usage

the mapping of single letters to prefixes and suffixes are found in `shorthand/_3x10_prefix_suffix.json`

![image](https://github.com/mjdi/wordshrink/assets/24360385/db0fafa4-77ab-4448-b2cd-a2586db82e09)

Clone the repo in powershell

`git clone https://github.com/mjdi/wordshrink`

cd into the repo

`cd wordshrink`

create a virtual environment, activate it, and install requirments.txt

`virtualenv venv`

`.\venv\Scripts\activate.ps1`

`pip install -r requirments.txt`

run `python shorthand\generate.py` to generate the prefix|root|suffix list of all 7 letters or longer english 50k words from https://github.com/hermitdave/FrequencyWords/tree/master/content/2016/en

TODO: create command line options to adjust these parameters, like root word length (3 letters minus vowels)

![image](https://github.com/mjdi/wordshrink/assets/24360385/0870e769-f833-4a07-b351-a56b1cfb4dfa)

run `python engine.py` in powershell to start shrinking words via holding Space and stacking letters into a stroke,

![image](https://github.com/mjdi/wordshrink/assets/24360385/e3adc07c-c1bf-4e77-a25b-ecedeb2839eb)

semicolon (`;`) is a prefix and suffix delineator on press and release, ex. unimportantly == ui;⬇️prt⬆️ty
