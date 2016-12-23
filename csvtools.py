import re
import numpy as np
import pandas as pd
import itertools

from responseparser import read_quantity


# Remove anything that isn't a character, number, or space from the string
def remove_symbols(string, repl=''):
    return re.sub(r'[^a-zA-Z0-9\s]', repl, string)


def translate_quantity(row):
    string = row['quantity'].lower().strip()

    # Remove anything in brackets
    string = re.sub(r'\[.*\]', '', string)

    return read_quantity(string)

    #
    # # Match '3DZ', '10PK', etc
    # match = re.match(r'(\d+)(dz|pk)', string, re.IGNORECASE)
    # if match:
    #     num = int(match.group(1)) if match.group(1) else 1
    #     mult = 12 if match.group(2).lower() == 'dz' else 1
    #     return num * mult
    #
    # # Match 'PK6', 'PK10', etc
    # match = re.match(r'(pk|p)(\d+)', string, re.IGNORECASE)
    # if match:
    #     return int(match.group(2))
    #
    # # Ambiguous quantities
    # if string in ['bx', 'cs', 'pk', 'st']:
    #     quant = read_quantity(str(row['features']))
    #     if quant:
    #         return quant
    #     else:
    #         print('(SKU: %s) Could not translate quantity, guessing \'1\': %s' % (row['sku'], row['features']))
    #         return 1


if __name__ == '__main__':
    df = pd.read_csv('tigerchef.csv')

    for i, row in df.iterrows():
        # Translate the quantity
        df.loc[i, 'quantity'] = translate_quantity(row)

    df.to_csv('tigerchef_mod.csv')


