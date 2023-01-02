import pandas as pd
import glob
from tqdm import tqdm

def replace_file_strings(fin, fout, replacements: dict):
    with open(fin, 'r') as infile, open(fout, 'w') as outfile:
        for line in infile:
            for src, target in replacements.items():
                if not isinstance(target, str):
                    target = str(target)
                line = line.replace(src, target)
            outfile.write(line)
    return

def mass_produce(f_txt, f_brd):
    """
    Currently, mass-production template BRDs and resulting
    BRDs will be saved to the same directory.
    """
    df = pd.read_csv(f_txt, sep = '\t')
    varcol, transcol = df.columns[0], df.columns[2]
    repl = {k: v for k, v in zip(df[varcol], df[transcol])}
    f_brd_out = f_brd.replace('_placeholder', '')
    replace_file_strings(f_brd, f_brd_out, repl)
    return

fs_txt = glob.glob('translated_files/mass_production/*.txt')

for f_txt in tqdm(fs_txt):
    f_brd = f_txt.replace('/mass_production/', '/FinalBRDs/')
    f_brd = f_brd.replace('.txt', '.brd')
    f_brd = f_brd.replace('_massproduction', '_placeholder')
    mass_produce(f_txt, f_brd)
