import sys
import keyboard
from enum import Enum

# constants
class Prog_State(Enum):
    DEF = 1, # default
    SHD = 2, # shorthand

_3x5_keys = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o',
             'p','q','r','s','t','u','v','w','x','y','z',',','.',';',"'"]

# globals
prog_state = Prog_State.DEF
space_held = False
_3x5_keys_held = [0] * len(_3x5_keys)
_3x5_key_sequence = [] # list of key names that have been pressed in order


#{'alt', 'alt gr', 'ctrl', 'left alt', 'left ctrl', 'left shift', 
#  'left windows', 'right alt', 'right ctrl', 'right shift', 'right windows',
#  'shift', 'windows'}

modifiers = list(keyboard.all_modifiers)
modifiers_held = [0] * len(modifiers)

# functions
def handle_shorthand(shorthand):
    print('_'.join(shorthand))
    return

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
        global _3x5_keys_held
        global _3x5_key_sequence
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

            if sum(_3x5_keys_held) > 0: # still some alphas held
                for key in _3x5_key_sequence:
                    keyboard.press_and_release(key) # type the sequecne
                    
            # reset
            _3x5_key_sequence.clear()
            keys_held = [0] * len(_3x5_keys_held)

            prog_state = Prog_State.DEF
            return

        # guard clause to handle 3x5 keys
        if event.name in _3x5_keys:
            if prog_state == Prog_State.SHD:
                if event.event_type == 'down': # on intial down press
                    if _3x5_keys_held[_3x5_keys.index(event.name)] == 0:
                        _3x5_key_sequence.append(event.name)
                    _3x5_keys_held[_3x5_keys.index(event.name)] = 1 # ignore holding
                else: # on release
                    _3x5_keys_held[_3x5_keys.index(event.name)] = False
                    if sum(_3x5_keys_held) == 0: # only space is held
                        handle_shorthand(_3x5_key_sequence)
                        _3x5_key_sequence.clear()
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
        print(error)
        sys.exit(0)


if __name__ == '__main__':

    keyboard.hook(on_key, suppress=True)
    
    keyboard.wait(100000)