"""
Take hand-coded Google Sheet and parse it into a JS function for translation according to MB's template.
"""

import pandas as pd
import re

SHEET_ID = 'private'
SHEET_NAME = 'Sheet1'

CHARS_TO_ESCAPE = "'"+'"'  # Add here all characters that you want to escape
CHARS_TO_ESCAPE_RE = (  # This whole clause is equivalent to: CHARS_TO_ESCAPE_RE = r"(?<!\\)(@|\[)"
    r"(?<!\\)("
    + r"|".join(map(lambda value: re.escape(value), CHARS_TO_ESCAPE))
    + r")"
)

def get_hand_coded_data():
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'
    df = pd.read_csv(url)
    return df

def sanitize(s):
    res = re.sub(CHARS_TO_ESCAPE_RE, r"\\\1", s)
    return res

df = get_hand_coded_data()
print(df)

with open('example.js.txt', 'w') as outf:
    outf.write(
"""
var translate = (function(){
	var translations = {
"""
    )
    for index, row in df.iterrows():

        outf.write(f"""
'{sanitize(row.English)}' : {{
            'en-US': '{sanitize(row.English)}',
            'de-de': '{sanitize(row.German)}'
        }},
"""
        )

    outf.write(
""" 
	};

	return function translate(key, lang, vars) {
		vars = vars || {};
		let translation = translations[key] ? translations[key][lang] : key;
		for (let varName in vars) {
			translation = translation.replaceAll(varName, translate(vars[varName], lang))
		}
		return translation
	};
})();    
""")

