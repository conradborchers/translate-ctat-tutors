from ctypes.util import find_library

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

STOPWORDS = stopwords.words('english')

PROJECT_DIR = '/home/cbo/Desktop/translate-ctat-tutors/'
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
    s = re.sub('[^0-9a-zA-Z_\'\s*/+-äöüÄÖÜß!?\.]', '', s) #keep alnum, operators, umlauts, and apostrophe
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
            translation = ts.google(the_clean_phrase, from_language='en', to_language='de')
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
        f.write(f"{signature}\t{signature+'_english'}\t{signature+'_german'}\t\n")
        for k in var_phrase_map.keys():
            en = var_phrase_map[k]
            de = var_translation_map.get(k)
            if de is None:
                de = '### FEHLENDE UEBERSERSETZUNG ###' # missing translation if API fails, currently no re-tries, need to hand-code 
            else:
                de = de.replace('\t', '') # TODO: Some translation remained with tabs for some reason
            f.write(f"{k}\t{en}\t{de}\n")
    
    save_translations(repeated_translations)
    return

print("Transforming brd files...")
fs_brd = glob.glob(PROJECT_DIR+'files/FinalBRDs/*')
for infile in tqdm(fs_brd):
    outfile_brd = infile.replace('/files/FinalBRDs/', '/translated_files/FinalBRDs/').replace('.brd', '_placeholder.brd')
    outfile_massprod = infile.replace('/files/FinalBRDs/', '/translated_files/mass_production/').replace('.brd', '_massproduction.txt')
    process_file(infile, outfile_brd, outfile_massprod)
