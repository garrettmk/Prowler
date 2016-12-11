import re
import numpy as np
import pandas as pd
import itertools


# Remove anything that isn't a character, number, or space from the string
def remove_symbols(string, repl=''):
    return re.sub(r'[^a-zA-Z0-9\s]', repl, string)


def translate_quantity(row):
    string = row['quantity'].lower().strip()

    if string in ['ea', 'each', 'ft', 'rl']:
        return 1

    if string == 'pr':
        return 2

    if string == 'dz':
        return 12

    # Match '3DZ', '10PK', etc
    match = re.match(r'(\d+)(dz|pk)', string, re.IGNORECASE)
    if match:
        num = int(match.group(1)) if match.group(1) else 1
        mult = 12 if match.group(2).lower() == 'dz' else 1
        return num * mult

    # Match 'PK6', 'PK10', etc
    match = re.match(r'(pk|p)(\d+)', string, re.IGNORECASE)
    if match:
        return int(match.group(2))

    # Ambiguous quantities
    if string in ['bx', 'cs', 'pk', 'st']:
        quant = read_quantity(str(row['features']))
        if quant:
            return quant
        else:
            print('(SKU: %s) Could not translate quantity, guessing \'1\': %s' % (row['sku'], row['features']))
            return 1


if __name__ == '__main__':
    df = pd.read_csv('etundra.csv')

    for i, row in df.iterrows():

        # Replace regular price with bulk price, if available
        if row['bulk'] in [np.nan, 'null', '', None]:
            pass
        else:
            df.loc[i, 'price'] = row['bulk']

        # Fill in the quantity
        df.loc[i, 'quantity'] = translate_quantity(row)

    df.to_csv('etundra_mod.csv')


