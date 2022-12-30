from ctypes.util import find_library

import time

import glob
import json

import xml.etree.ElementTree as ET

from timeit import repeat

from bs4 import BeautifulSoup
from tqdm import tqdm

import translators as ts
ts._google.language_map 

import sys
import xml.etree.ElementTree as ET

import re
from nltk.corpus import stopwords

import pandas as pd

import deepl

### 

DEBUG = False # Only translate one example file
USE_DEEPL = True # Translate via commercial deepl API
FILL_HANDCODING = True # Use hand-coded translation dictionary

# SET THESE VARIABLES BEFORE RUNNING THE TRANSLATION ROUTINE

PROJECT_DIR = '/home/cbo/Desktop/translate-ctat-tutors/'
TRANSLATION_DICT = PROJECT_DIR+'translations-stoich-en-to-de-deepl-handcode-v1-missing.json'
HANDCODING_CSV = PROJECT_DIR+'Stoich-En-De-Hand-V1.csv'

#TARGET_LANG = 'iw' # hebrew
#LANGUAGE_STRING = 'hebrew' # generic string to identify language

TARGET_LANG = 'de' # german
LANGUAGE_STRING = 'german' # generic string to identify language

TOKEN_DIR = PROJECT_DIR+'token.txt'
GLOSSARY_DIR = PROJECT_DIR+'glossary-stoichiometry-en-de-sascha-round-3.csv'

print(f"""
Summary of session settings:
Only translate one file (debug mode): {DEBUG};
Primarily fill translations via hand-coded file: {FILL_HANDCODING};
Using Deepl and not free Google API: {USE_DEEPL};
We are in directory: {PROJECT_DIR};
There is a Deepl token txt file at: {TOKEN_DIR};
There is a custom Deepl glossary csv file at: {GLOSSARY_DIR};
There is a hand-coded translation csv file at {HANDCODING_CSV};
Signature for persisting storage of translations: {TRANSLATION_DICT};
We translate from English to: {TARGET_LANG}; which is saved with the signature: {LANGUAGE_STRING};
""")

input('Press any key to continue with these settings.')

###

## Deepl Functions ##

def read_token(file_path = TOKEN_DIR):
    '''Reads in bearer tokens from a file path'''
    with open(file_path, "r") as f:
        for line in f:
            auth_key = line.strip()
            break
    return auth_key

def read_glossary(file_path):
    with open(file_path, 'r',  encoding='utf-8') as csv_file:
        csv_data = csv_file.read()  # Read the file contents as a string
        glossary = translator.create_glossary_from_csv(
            "CSV glossary",
            source_lang="EN",
            target_lang="DE",
            csv_data=csv_data,
        )
    return glossary

def translate_text(input_text, source_lang="EN", target_lang='DE', formality='less', glossary=None):
    try:
        result = translator.translate_text(input_text, source_lang=source_lang, target_lang=target_lang, formality=formality, glossary=glossary)
        return '' if result.text is None else result.text
    except:
        return '### ERROR ###'

auth_key = read_token()
translator = deepl.Translator(auth_key)
stoich_glossary = read_glossary(GLOSSARY_DIR)

###

STOPWORDS = stopwords.words('english')

def load_translations(f=TRANSLATION_DICT):
    with open(f, 'r') as handle:
        d_in = json.load(handle)
    return d_in

def save_translations(d_out, f=TRANSLATION_DICT):
    with open(f, 'w') as handle:
        json.dump(d_out, handle, ensure_ascii = False)
    return

def load_hand_coding(f=HANDCODING_CSV, target_lang='german'):
    df = pd.read_csv(f)
    df.drop_duplicates(subset=['english'], inplace=True)
    ans = {k: v for k, v in zip(df['english'], df[target_lang])}
    return ans

# Store repeated translations as there is usually a lot to translate in BRDs -> reduce runtime
if FILL_HANDCODING:
    try:
        repeated_translations = load_hand_coding() 
    except:
        print('Failed to load hand-coding file. Exiting...')
        exit()
else:
    try:
        repeated_translations = load_translations() 
    except:
        repeated_translations = dict() # If there is not file in DIR
        save_translations(repeated_translations)

# -- HTML --
print("Transforming HTML files...")

# List HTML files
fs_html = glob.glob(PROJECT_DIR+'files/HTML/*')
if DEBUG:
    fs_html = [PROJECT_DIR+'files/HTML/stoichTutor1.html',
               PROJECT_DIR+'files/HTML/stoichTutor2.html',
               PROJECT_DIR+'files/HTML/stoichTutor3.html',
               PROJECT_DIR+'files/HTML/stoichTutor4.html',
               PROJECT_DIR+'files/HTML/stoichTutor5.html',
               PROJECT_DIR+'files/HTML/stoichTutor6.html',
               PROJECT_DIR+'files/HTML/stoichTutor7.html',
               PROJECT_DIR+'files/HTML/stoichTutor8.html',
               PROJECT_DIR+'files/HTML/stoichTutor9.html',
               PROJECT_DIR+'files/HTML/stoichTutor10.html',
               PROJECT_DIR+'files/HTML/stoichTutor11.html']

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
                    try:
                        found.string.replace_with(repeated_translations[found.string])
                    except:
                        continue
                else:
                    try:
                        if USE_DEEPL:
                            translation = translate_text(found.string, source_lang="EN", target_lang='DE', formality='less', glossary=stoich_glossary)
                        else:
                            translation = ts.google(found.string, from_language='en', to_language=TARGET_LANG)
                        repeated_translations[found.string] = translation
                        found.string.replace_with(translation)
                    except:
                        continue
        outpath = f_str.replace('/files/HTML/', '/translated_files/HTML/').replace('.html', '_'+LANGUAGE_STRING+'.html')
        save_translations(repeated_translations)
        with open(outpath, 'w') as outfile:
            outfile.write(str(soup))

# -- BRD -- -> Mass-production variable placeholder strategy

def clean_name(s, convert_to_lower=True):
    s = re.sub('<[^<]+?>', '', s) #markup
    s = re.sub('[^0-9a-zA-Z_\s]', '', s) #keep alnum
    s = re.sub('\t\n\r', '', s) #remove tab, line break, carriage return
    s = ' '.join(s.split()) #remove redundant whitespace
    return s.lower() if convert_to_lower else s

def clean_phrase(s, convert_to_lower=False):
    # TODO (check if html references should be preserved in translation)
    s = re.sub('<[^<]+?>', '', s) #markup
    s = re.sub('[^0-9a-zA-Z_\'\s*/+-äöüÄÖÜß!?\.\u0590-\u05fe]', '', s) #keep alnum, operators, umlauts, hebrew, and apostrophe
    s = re.sub('\t\n\r', '', s) #remove tab, line break, carriage return
    s = ' '.join(s.split()) #remove redundant whitespace
    return s.lower() if convert_to_lower else s

def make_var(phrase, signature='_', keep_n_words=4):
    if(phrase is None or phrase == ''):
        return ''
    h = signature + '_' + '_'.join([word for word in clean_name(phrase).split(' ') if word not in STOPWORDS][:keep_n_words])
    v = '%(' + str(h) + ')%'

    the_clean_phrase = clean_phrase(phrase)
    var_phrase_map[v] = the_clean_phrase

    # Translate, translations will be stored with same key as English text in different dict()
    if the_clean_phrase in repeated_translations:
        var_translation_map[v] = repeated_translations[the_clean_phrase]
    else:
        try:
            if USE_DEEPL:
                translation = translate_text(the_clean_phrase, source_lang="EN", target_lang='DE', formality='less', glossary=stoich_glossary)
            else:
                translation = ts.google(the_clean_phrase, from_language='en', to_language=TARGET_LANG)
            translation = clean_phrase(translation) # Clean translation
            repeated_translations[the_clean_phrase] = translation
            var_translation_map[v] = translation
        except:
            pass
    return v

def iterate_generic(tag: str, root):
    """
    TODO Review
    Only translate first input (i.e., prolem statement) for now.
    """
    count = 1
    for element in root.iter(tag):
        if tag == 'Input' and count > 1:
            continue
        if tag == 'Input':
            txt = element[0].text
        else:
            txt = element.text
        if txt is None or txt.startswith("%("):
            continue
        else:
            if tag == 'Input':
                element[0].text = make_var(txt, signature=tag+'_'+str(count))
            else:
                element.text = make_var(txt, signature=tag+'_'+str(count))
        count += 1

def process_file(infile, outfile_brd, outfile_massprod):
    global tree; tree = ET.parse(infile)
    global root; root = tree.getroot()
    global var_phrase_map; var_phrase_map = dict()
    global var_translation_map; var_translation_map = dict()
    
    tags = ['hintMessage', 'buggyMessage', 'successMessage', 
            'label', 'Input']
    # tags += ['productionRule'] # exclude for now
    for tag in tags:
        iterate_generic(tag, root)
    
    tree.write(outfile_brd)
    
    signature = infile.split('/')[-1].split('.brd')[0]
    with open(outfile_massprod, "w") as f:
        f.write(f"{signature}\t{signature+'_english'}\t{signature+'_'+LANGUAGE_STRING}\t\n")
        for k in var_phrase_map.keys():
            en = var_phrase_map[k]
            de = var_translation_map.get(k)
            if de is None:
                de = '### MISSING TRANSLATION ###' # missing translation if API fails, currently no re-tries, need to hand-code 
            else:
                de = de.replace('\t', '') # TODO: Some translation remained with tabs for some reason
            f.write(f"{k}\t{en}\t{de}\n")
    save_translations(repeated_translations)
    return

print("Transforming brd files...")
fs_brd = glob.glob(PROJECT_DIR+'files/FinalBRDs/*')
if DEBUG:
    fs_brd = [PROJECT_DIR+'files/FinalBRDs/ChemPT_1T_01_PU.brd',
              PROJECT_DIR+'files/FinalBRDs/ChemPT_1T_02_PU.brd',
              PROJECT_DIR+'files/FinalBRDs/ChemPT_1T_06_PU.brd',
              PROJECT_DIR+'files/FinalBRDs/ChemPT_2T_03_PU.brd',
              PROJECT_DIR+'files/FinalBRDs/ChemPT_2T_04_PU.brd',
              PROJECT_DIR+'files/FinalBRDs/ChemPT_2T_33_PU.brd',
              PROJECT_DIR+'files/FinalBRDs/ChemPT_2T_24_PU.brd',
              PROJECT_DIR+'files/FinalBRDs/ChemPT_2T_32_PU.brd',
              PROJECT_DIR+'files/FinalBRDs/ChemPT_2T_59_PU.brd',
              PROJECT_DIR+'files/FinalBRDs/ChemPT_3T_26_PU.brd',
              PROJECT_DIR+'files/FinalBRDs/ChemPT_3T_62_PU.brd'] 
for infile in tqdm(fs_brd):
    outfile_brd = infile.replace('/files/FinalBRDs/', '/translated_files/FinalBRDs/').replace('.brd', '_'+LANGUAGE_STRING+'_placeholder.brd')
    outfile_massprod = infile.replace('/files/FinalBRDs/', '/translated_files/mass_production/').replace('.brd', '_'+LANGUAGE_STRING+'_massproduction.txt')
    process_file(infile, outfile_brd, outfile_massprod)

print(f"Creating accessible hand-coding file for {TRANSLATION_DICT}")
outf_dict = TRANSLATION_DICT.replace('.json', '-handcoding.csv')
print(f"Saving to {outf_dict}")
df_phrase = pd.DataFrame(repeated_translations.items())
df_phrase.columns = ['english', LANGUAGE_STRING]
out = df_phrase\
    .groupby('english')\
    .agg({LANGUAGE_STRING: pd.unique})\
    .reset_index()
out.to_csv(outf_dict, index=False)
