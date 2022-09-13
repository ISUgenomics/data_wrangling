# -*- coding: utf-8 -*-

import sys			# to manage inline arguments
import argparse			# to convert python script into program with options
import pandas as pd		# to easily parse json object and filter out data; require installation with conda or pip
from datetime import datetime	# to create unique tag into the default output filename
import csv			# to read any column-like text file

sep=','

def get_delimiter(text_file: str) -> str:
    with open(text_file, 'r') as csvfile:
        delimiter = str(csv.Sniffer().sniff(csvfile.read()).delimiter)
        return delimiter


def load_input_file(input_file):

    format = input_file.split('.')[1]
    if format == 'xlsx':
        return pd.read_excel(input_file, index_col=None, header=0)  # read xlsx file with pairs of matched labales (.xlsx)
    else:
        delim = get_delimiter(input_file)
        sep = delim
        return pd.read_csv(input_file, sep=delim, index_col=None, header=0)  # read text file separated with any delimiter


def merge_data_by_labels(first_file, second_file, matching_cols, error_value, outfile, output_format):

    tag = datetime.now().strftime("-%d-%m-%Y-%H%M%S")
###-- read inputs and create data structure

    matching_cols = matching_cols.split(',')
    file1 = load_input_file(first_file)
    file2 = load_input_file(second_file)
    cols1 = file1.columns.tolist()
    cols2 = file2.columns.tolist()
    lab1 = matching_cols[0]
    lab2 = matching_cols[1]
    
    # if provided indexes of cols, then find their headers
    if matching_cols[0].isnumeric():  
        lab1 = cols1[int(matching_cols[0])]
    if matching_cols[1].isnumeric():
        lab2 = cols2[int(matching_cols[1])]
        
###-- add all columns from file2 into file1 based on matching columns
    cols2.remove(lab2)
    [file1.insert(len(cols1)+idx, i, '') for idx, i in enumerate(cols2)]
    for idx, i in file1[lab1].iteritems():
        val = file2[file2[lab2] == i]
        if len(val) > 0:
            for col in cols2:
                file1.at[idx, col] = val[col].values[0]
        else:
            for col in cols2:
                file1.at[idx, col] = error_value
#    print(file1)

###-- export output data_file
    if outfile == 'data_output':
        outfile += tag        
    if output_format == 1:
        file1.to_csv(outfile+'.csv', sep=',', encoding='utf-8')     # output in CSV format
    elif output_format == 2:					
        file1.to_excel(outfile+'.xlsx', index=False, header=True)   # output in xlsx format (Excel)
    else:
        file1.to_csv(outfile+'.csv', sep=sep, encoding='utf-8')


###-- add options to the argument parser to make it easier to customize and run the script from the command line
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='data_matcher.py',
        description="""Merge data of two files using matching column.\n 
                       Requirements: python3, pandas, openpyxl, csv""",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=''
    )
    parser.add_argument(
        '-i', '--data-file-1',
        help='[string] input multi-col file',
        metavar='file1',
        dest='file1',
        required=True
    )
    parser.add_argument(
        '-m', '--data-file-2',
        help='[string] merge multi-col file',
        metavar='file2',
        dest='file2',
        required=True
    )
    parser.add_argument(
        '-c', '--matching-columns',
        help='list of the same column of two files, e.g., 0,5 or label1,label2 \ncol index starting from 0 [int] or headers',
        metavar='cols',
        required=True,
        dest='cols'
    )
    parser.add_argument(
        '-e', '--error-value',
        help='provide custom value for missing data',
        metavar='missing',
        default=-9999.99,
        dest='error'
    )
    parser.add_argument(
        '-o', '--output-datafile',
        help='provide custom name for the output data_file',
        metavar='outfile',
        type=str,
        default='data_output',
        dest='outfile'
    )
    parser.add_argument(
        '-f', '--output-format',
        help='select format for output file: 0 - original, 1 - csv, 2 - xlsx',
        metavar='format',
        type=int,
        default=0,
        dest='format'
    )

###-- print example of usage and help message when script is run without required arguments
    if len(sys.argv) < 3:
        parser.print_help()
        print("\nUSAGE:\n	e.g., python3 merge_data.py -i input_file -m merge_file -c 1,5 \n")
        sys.exit(1)

    args = parser.parse_args()
    merge_data_by_labels(args.file1, args.file2, args.cols, args.error, args.outfile, args.format)
