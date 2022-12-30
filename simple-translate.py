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

TARGET_LANG = 'de' # german
LANGUAGE_STRING = 'german' # generic string to identify language

PROJECT_DIR = '/home/cbo/Desktop/translate-ctat-tutors/'

TOKEN_DIR = PROJECT_DIR+'token.txt'
GLOSSARY_DIR = PROJECT_DIR+'glossary-stoichiometry-en-de-sascha-round-3.csv'

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

inputs = [
"Example sentence 1",
"Example sentence 2"
]

for text in inputs:
    s = translate_text(text, source_lang="EN", target_lang='DE', formality='less', glossary=stoich_glossary)
    print(s)
