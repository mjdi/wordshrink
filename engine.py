import os
import pathlib
import keyboard
from enum import Enum
import json

import shorthand.generate as gn

exec_dir = os.path.dirname(os.path.realpath(__file__))
shorthands_filename = gn.shorthands_en_50k_filename # gn.shorthands_en_full_filename 
shorthands_filepath = pathlib.Path(exec_dir) / 'shorthand' / shorthands_filename

# constants
class Prog_State(Enum):
    DEF = 1, # default
    SHD = 2, # shorthand

_3x10_keys = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o',
             'p','q','r','s','t','u','v','w','x','y','z',',','.',';',"'"]

### for qwerty the semi-colon key shares the same column as p and forward slash
### so we might need to make concessions for that

### for colemak dh we make the comma key correspond to the 'o' key

PREFIX_DELIM_KEY = ";" # types on press & release to delimit prefix|root & root|suffix respectively
SUFFIX_DELIM_KEY = "'" # types on press & release to delimit root|suffix & prefix|root respectively

# globals
prog_state = Prog_State.DEF
space_held = False
_3x10_keys_held = [0] * len(_3x10_keys)
_3x10_key_sequence = [] # list of key names that have been pressed in order


#{'alt', 'alt gr', 'ctrl', 'left alt', 'left ctrl', 'left shift', 
#  'left windows', 'right alt', 'right ctrl', 'right shift', 'right windows',
#  'shift', 'windows'}

modifiers = list(keyboard.all_modifiers)
modifiers_held = [0] * len(modifiers)

# functions
def get_handle_shorthand_fn():

    with open(shorthands_filepath, 'r') as f:
        shorthand_to_words_dict = json.load(f)

    def handle_shorthand(_3x10_key_sequence):
        seq = "".join(_3x10_key_sequence)

        shorthand = ""
    
        if PREFIX_DELIM_KEY not in seq and SUFFIX_DELIM_KEY not in seq:
            # root word only with no prefixes or suffixes
            shorthand = gn.SH_DELIM + seq + gn.SH_DELIM
        else:
            # prefix|root|suffix, but may be missing one of prefix or suffix, thus a delimiter is missing
            shorthand = seq.replace(PREFIX_DELIM_KEY, gn.SH_DELIM).replace(SUFFIX_DELIM_KEY, gn.SH_DELIM)

            if shorthand.count(gn.SH_DELIM) == 1:
                # add delimiter to whichever side is missing it
                if PREFIX_DELIM_KEY not in seq:
                    shorthand = gn.SH_DELIM + shorthand
                else:
                    shorthand = shorthand + gn.SH_DELIM

        if shorthand in shorthand_to_words_dict:
            word = list(shorthand_to_words_dict[shorthand][0].keys())[0] # get first word, most common
            print(f'Word found for shorthand: {shorthand} -> {word}') 
            # TODO: keep track of previously typed spaces and use that to determine whether to add a space
            keyboard.write(' ' + word + ' ')
        else:
            print(f'No word found for shorthand: {shorthand}')
 
        return
    
    return handle_shorthand


handle_shorthand_fn = get_handle_shorthand_fn()


def create_modifiers_string():
    modifier_string = ''
    for i in range(len(modifiers)):
        if modifiers_held[i] == 1:
            modifier_string += modifiers[i] + '+'
    return modifier_string

def on_key(event):
    try: 
        global prog_state
        global space_held
        global _3x10_keys_held
        global _3x10_key_sequence
        global modifiers_held

        # guard clauses to handle Space functionality
        if prog_state == Prog_State.DEF and event.name == 'space' \
                                        and event.event_type == 'down':
            # enter shorthand mode
            space_held = True
            prog_state = Prog_State.SHD
            return

        if prog_state == Prog_State.SHD and event.name == 'space' \
                                        and event.event_type == 'up':
            # press all necessary keys
            keyboard.press_and_release('space') # input a single space
            space_held = False

            if sum(_3x10_keys_held) > 0: # still some alphas held
                for key in _3x10_key_sequence:
                    keyboard.press_and_release(key) # type the sequecne
                    
            # reset
            _3x10_key_sequence.clear()
            keys_held = [0] * len(_3x10_keys_held)

            prog_state = Prog_State.DEF
            return

        # guard clause to handle 3x10 keys
        if event.name in _3x10_keys:
            if prog_state == Prog_State.SHD:
                if event.event_type == 'down': # on intial down press
                    if _3x10_keys_held[_3x10_keys.index(event.name)] == 0:
                        _3x10_key_sequence.append(event.name)
                    _3x10_keys_held[_3x10_keys.index(event.name)] = 1 # ignore holding
                else: # on release
                    if event.name == PREFIX_DELIM_KEY or event.name == SUFFIX_DELIM_KEY:
                        _3x10_key_sequence.append(event.name) # add delimiter on release also
                    _3x10_keys_held[_3x10_keys.index(event.name)] = False
                    if sum(_3x10_keys_held) == 0: # only space is held
                        handle_shorthand_fn(_3x10_key_sequence)
                        _3x10_key_sequence.clear()
            else: # prog_state == Prog_State.DEF
                if event.event_type == 'down':  
                    keyboard.send(create_modifiers_string()+event.name, event.event_type)

            return
        
        # guard clause to handle modifiers
        if event.name in modifiers:
            if event.event_type == 'down':
               modifiers_held[modifiers.index(event.name)] = 1
            else:
                modifiers_held[modifiers.index(event.name)] = 0
            return
        
        # default case
        if event.event_type == 'down': # prog_state == Prog_State.DEF
            keyboard.send(create_modifiers_string()+event.name, event.event_type)


    except ValueError as error:
        import sys
        print(error)
        sys.exit(0)


if __name__ == '__main__':

    keyboard.hook(on_key, suppress=True)
    
    keyboard.wait(100000)