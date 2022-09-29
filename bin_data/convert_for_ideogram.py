# -*- coding: utf-8 -*-
import os                       # to manage paths
import sys                      # to manage inline arguments
import argparse                 # to convert python script into program with options
import pandas as pd             # to easily parse json object and filter out data; require installation with conda or pip
import numpy as np              # to parse advanced numerical data structures; require installation
import re                       # to use regular expressions
import json                     # to save data into json format


COLORS = {0: 'gneg', 1: 'gpos25', 2: 'gpos33', 3: 'gpos50', 4: 'gpos66', 5: 'gpos75', 6: 'gpos100', 7: 'acen', 8: 'gvar'}


def extract_digits(txt):
    return '-'.join([s for s in re.findall(r'\d+', txt) if s.isdigit()])


def convert_for_ideogram(input_file, labels, ranges, arms, bands, values):

    ideo = {}
    data_df = pd.read_csv(input_file)
    mean = data_df.iloc[:, 2:].mean().astype(int).apply(lambda x: x*2).to_dict()	# double mean of each numerical column
    keys = list(data_df.columns)
    to_drop = [keys[labels], keys[ranges]]
    try:
        to_drop.append(keys[arms])
        to_drop.append(keys[bands])
    except:
        print('')
        
    if values == None:
        values = [x for x in keys if x not in to_drop]

    color_dict = {}
    for val in values:
        colors = {}
        for num, i in enumerate([0.14, 0.28, 0.42, 0.56, 0.70, 0.84, 1.00, 1.20]):
            colors[i*mean[val]] = COLORS[num]
        color_dict[val] = colors
        ideo[val] = {'chrBands':[]}
    
    arm = 'p'    
    for index, row in data_df.iterrows():
        idx = extract_digits(row[keys[labels]])
        try:
            arm = row[keys[arms]]
            band = row[keys[bands]]
        except:
            band = arm+idx+"-"+str(index)
            
        position = row[keys[ranges]].split('-')
        start = position[0]
        if len(position) > 1:
            end = position[1]
        else: 
            end = start + data_df[keys[ranges]].iloc[index+1] - 1
            
        for num, val in enumerate(values):
            color = 'gvar'
            colors = color_dict[val]
            for n, est in enumerate(colors.keys()):
                if row[val] < est:
                    color = colors[est]
                    break
            
            string = str(idx)+' '+str(arm)+' '+str(band)+' '+str(start)+' '+str(end)+' '+str(start)+' '+str(end)+' '+str(color)
            ideo[val]['chrBands'].append(string)

    for value in ideo:
        with open('data-'+value+'.json', 'w') as f:
            json.dump(ideo[value], f)
        
    
    
###-- add options to the argument parser to make it easier to customize and run the script from the command line
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='convert_for_ideogram.py',
        description="""Convert data to idogram format.\n 
                       Requirements: python3, pandas""",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=''
    )
    parser.add_argument(
        '-i', '--data-source',
        help='[string] input multi-col file',
        metavar='input',
        dest='input',
        required=True
    )
    parser.add_argument(
        '-l', '--labels-col',
        help='[string] index of column with labels',
        metavar='label',
        dest='label',
        type=int,
        required=True
    )
    parser.add_argument(
        '-r', '--ranges-col',
        help='[string] index of column with ranges',
        metavar='range',
        dest='range',
        type=int,
        required=True
    )    
    parser.add_argument(
        '-a', '--arms-col',
        help='[string] index of column with chromosome arms annotation',
        metavar='arm',
        dest='arm',
        type=int,
        default=None
    )     
    parser.add_argument(
        '-b', '--bands-col',
        help='[string] index of column with bands annotation (names)',
        metavar='band',
        dest='band',
        type=int,
        default=None
    ) 
    parser.add_argument(
        '-v', '--values-col',
        help='[string] list of indices of numerical columns to have color assigned',
        metavar='vals',
        dest='vals',
        type=list,
        default=None
    )
        
###-- print example of usage and help message when script is run without required arguments
    if len(sys.argv) < 2:
        parser.print_help()
        print("\nUSAGE:\n")
        print("e.g., minimal required inputs:\n         python3 convert_for_ideogram.py -i input_file -l 0 -r 1")
        sys.exit(1)

    args = parser.parse_args()
    convert_for_ideogram(args.input, args.label, args.range, args.arm, args.band, args.vals)