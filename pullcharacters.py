#!/usr/bin/python

import urllib.request 
import json

import os
from os import listdir
from os.path import isfile, join

# Download the file from `url` and save it locally under `file_name`:
url = 'https://api.achaea.com/characters.json'
file_name = 'characters.json'
path = f'{os.environ["HOME"]}/repos/ttransendence/characters'

online = []
longestNameLen = 0
with urllib.request.urlopen(url) as response:
    # load up the json object
    jsondata = json.loads(response.read())
    #  print ('finished downloading list of characters')
    #  print(jsondata['count'])

    # parse out each character
    for c in jsondata['characters']:
        uri = c['uri']
        name = c['name']
        online.append(name.capitalize())
        if len(name) > longestNameLen: longestNameLen = len(name)
        with urllib.request.urlopen(uri) as charuri:
            charjson = json.loads(charuri.read())
            with open(f'{path}/{name}.json', 'w') as charfile:
                json.dump(charjson, charfile)

longestNameLen += 1
#  print ('finished characters')

# load up all the character files
allcharacters = [f for f in listdir(path) if isfile(join(path, f))]

characters = {}
fg_yellow = '<Fffff00>'
fg_red = '<Fff0000>'

with open(f'{path}/../character_highlights.tt', 'w') as hi:
    #  hi.write('#ticker {updatechardb} {#read character_highlights.tt} {60}\n\n')

    hi.write(f'#class chardatabase kill\n')
    hi.write(f'#class chardatabase open\n\n')
    for charName in online:
        with open(f'{path}/{charName}.json', 'r') as charfile:
            char = json.load(charfile)
            try:
                # create a dictionary of them
                #  print(char['name'])
                # could use 24 bit colors, format is <F000000> <FFFFFFF>
                color = '<848>' # the first '8' is to 'use previous value' or 'dont change'
                #  color = fg_yellow

                if 'city' in char:
                    city = char['city']
                    if 'ashtan'     in city: color = '<458>'            # underscore
                    if 'hashan'     in city: color = '<438>'            # underscore
                    if 'targossas'  in city: color = '<478>'
                    if 'underworld' in city: color = '<401>'
                    if 'mhaldor'    in city: color = '<418>'   
                    if 'cyrene'     in city: color = '<468>'   
                    if 'eleusis'    in city: color = '<199><428>'   
                    if '(hidden)'   in city: color = '<403>'            # underscore
                    if '(none)'     in city: color = color

                char['color'] = color
                characters[char['name']] = char

                priority = len(char['name'])
                # Can't use ACTION's because only the first one will fire.
                # SUBSITUTES fail because they break what goes after thier match
                # HIGHLIGHT 
                hi.write(f"#hi {{{char['name']}}} {{{color}}} {{{priority}}};\n")

            except Exception as inst:
                print(f'WTF??')
                print(f'---------------------')
                print(f'{file}')
                print(f'---------------------')
                print(inst.args)     # arguments stored in .args
                print(inst)          # __str__ allows args to be printed directly,
                                     # but may be overridden in exception subclasses
                break
    hi.write(f'#class chardatabase close;\n')
    hi.write(f'#class chardatabase save;\n')
    #  hi.write(f'#delay 2 {#class chardatabase clear};\n')
    hi.write('\n')

    hi.write('#var {chardb}\n')
    hi.write('{\n')
    for char in characters.items():
        hi.write(f'\t{{{char[0]}}} {{\n')

        hi.write(f'\t\t{{lvl}}\t\t{{{char[1]["level"]}}}\n')
        hi.write(f'\t\t{{city}}\t{{{char[1]["city"]}}}\n')
        hi.write(f'\t\t{{pvp}}\t\t{{{char[1]["player_kills"]}}}\n')
        hi.write(f'\t\t{{class}}\t{{{char[1]["class"]}}}\n')
        hi.write(f'\t\t{{xp}}\t\t{{{char[1]["xp_rank"]}}}\n')
        hi.write(f'\t\t{{explorer}} {{{char[1]["explorer_rank"]}}}\n')
        hi.write(f'\t\t{{color}}\t{{{char[1]["color"]}}}\n')

        hi.write('\t};\n\n')

    hi.write('};\n\n')



