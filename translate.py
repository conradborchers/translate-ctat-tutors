from ctypes.util import find_library

import glob
import json
import sys

from timeit import repeat

from bs4 import BeautifulSoup
from tqdm import tqdm

import translators as ts
ts._google.language_map 

PROJECT_DIR = '/home/<USER>/Desktop/translate-ctat-tutors/'
TRANSLATION_DICT = PROJECT_DIR+'translations-stoich-en-to-de.json'

def load_translations(f=TRANSLATION_DICT):
    with open(f, 'r') as handle:
        d_in = json.load(handle)
    return d_in

def save_translations(d_out, f=TRANSLATION_DICT):
    with open(f, 'w') as handle:
        json.dump(d_out, handle, ensure_ascii = False)
    return

# Store repeated translations as there is usually a lot to translate in BRDs -> reduce runtime
try:
    repeated_translations = load_translations() 
except:
    repeated_translations = dict() # If there is not file in DIR
    save_translations(repeated_translations)
    exit()

# -- HTML --
print("Transforming HTML files...")

# List HTML files
fs_html = glob.glob(PROJECT_DIR+'files/HTML/*')

# HTML tags to translate
elements = ['a', 'b', 'div']

# Run translation routine over all HTML files
SKIP_HTML = False
if not SKIP_HTML:
    for f_str in tqdm(fs_html):
        with open(f_str, 'r') as infile:
            soup = BeautifulSoup(infile, 'html.parser')
            for found in soup.findAll(elements):
                if found.string in repeated_translations:
                    found.string.replace_with(repeated_translations[found.string])
                else:
                    try:
                        translation = ts.google(found.string, from_language='en', to_language='de')
                        repeated_translations[found.string] = translation
                        found.string.replace_with(translation)
                    except:
                        continue
        outpath = f_str.replace('/files/HTML/', '/translated_files/HTML/').replace('.html', '_german.html')
        save_translations(repeated_translations)
        with open(outpath, 'w') as outfile:
            outfile.write(str(soup))

# -- BRD --
print("Transforming brd files...")

# List BRD files
fs_brd = glob.glob(PROJECT_DIR+'files/FinalBRDs/*')

# BRD tags to translate
elements = ['buggyMessage', 'hintMessage', 'successMessage', 'buggymessage', 'hintmessage', 'successmessage']

# Problem statements
# Problem statements are in value tags within input tags. However, if you replace all value tags
# throughout BRD files will corrupt some references that should not be changed. Therefore, I 
# match titles verbatim right now until I have found a better way of replacing them.
problem_statements = [
    "When you solve chemistry problems, you convert units to better",
    "Let's convert liters (L) to milliliters (mL) in this problem.",
    "Can you say how many grams of potatoes we would have?",
    "The World Health Organization's (WHO) recommended limit for arsenic",
    "Let's suppose we are responsible for a water supply that has become contaminated with alcohol (COH4).",
    "Let's calculate the number of molecules in a single gram (1.00) of H2",
    "Our result should have 3 significant figures",
    "Our result should have 5 significant figures",
    "Let's calculate the number of moles of Oxygen atoms in 15.95",
    "Can we calculate the number of moles of salt (NaCl) that are in a 350 ml solutio",
    "Let's say we have 125.0 mL of a Na3PO4 solution that has a concentration of 1.231",
    "Suppose we just discovered that it is possible to produce H2 with renewable energy source",
    "Let's figure out how many moles of O2 are in 1.216 kg COH4 and be sure our result has 4 significant figure"
]

# Run translation routine over all BRD files
# We need a parsed soup object to identify the right tags to replace and then replace the source code
# via string matching in order to preserve formating
SKIP_BRD = False
if not SKIP_BRD:
    for f_str in fs_brd:
        print(f'Running {f_str}...')
        with open(f_str, 'r') as infile:
            soup = BeautifulSoup(infile, 'html.parser')
        with open(f_str, 'r') as infile:
            raw = infile.read()
        for found in tqdm(soup.findAll(elements)):
            if found.string is None:
                continue
            if found.string in repeated_translations:
                raw = raw.replace(found.string.split('<a href')[0], repeated_translations[found.string]) # preserve hrefs, translator will omit them
            else:
                try:
                    translation = ts.google(found.string, from_language='en', to_language='de')
                    repeated_translations[found.string] = translation
                    raw = raw.replace(found.string.split('<a href')[0], translation) # preserve hrefs, translator will omit them
                except:
                    continue
        # Translate <value> inside <input> in separate loop to replace problem statements
        for found in tqdm(soup.findAll('value')):
            found_problem_statement = False
            for ps in problem_statements:
                try:
                    if ps.lower() in found.string.lower():
                        print('Found problem statement!')
                        found_problem_statement = True
                except:
                    continue
            if found_problem_statement:
                if found.string in repeated_translations:
                    raw = raw.replace(found.string.split('<a href')[0], repeated_translations[found.string]) # preserve hrefs, translator will omit them
                else:
                    try:
                        translation = ts.google(found.string, from_language='en', to_language='de')
                        repeated_translations[found.string] = translation
                        raw = raw.replace(found.string.split('<a href')[0], translation) # preserve hrefs, translator will omit them
                    except:
                        continue
            else:
                continue
        save_translations(repeated_translations)
        outpath = f_str.replace('/files/FinalBRDs/', '/translated_files/FinalBRDs/').replace('.brd', '_german.brd')
        with open(outpath, 'w') as outfile:
            outfile.write(raw)
