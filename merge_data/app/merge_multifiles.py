# -*- coding: utf-8 -*-

import sys			# to manage inline arguments
import argparse			# to convert python script into program with options
import logging                  # to provide verbosity level
from pathlib import Path        # to manage paths in the file system
from datetime import datetime	# to create unique tag into the default output filename
import csv			# to read any column-like text file
import pandas as pd		# to easily parse json object and filter out data; require installation with conda or pip


sep=','

def get_delimiter(text_file: str) -> str:
    with open(text_file, 'r') as csvfile:
        delimiter = str(csv.Sniffer().sniff(csvfile.read()).delimiter)
        return delimiter


def load_input_file(input_file):

    try:
        format = input_file.split('.')[1]
    except:
        format = ''
    if format == 'xlsx':
        return pd.read_excel(input_file, index_col=None, header=0)  # read xlsx file with pairs of matched labales (.xlsx)
    else:
        delim = get_delimiter(input_file)
        sep = delim
        return pd.read_csv(input_file, sep=delim, index_col=None, header=0)  # read text file separated with any delimiter


def merge_multifiles(files, matching_cols, keep_cols, error_value, outfile, output_format):

    tag = datetime.now().strftime("-%d-%m-%Y-%H%M%S")

    FILES = {}
    COLS = {}
    LABS = {}
    DF = pd.DataFrame()
    
###-- READ INPUTS AND CREATE DATA STRUCTURE

    #-- check correctness of the list of inputs
    path = Path(files)
    if path.is_file():
        with open(files) as file:
            files = [line.strip() for line in file]    
    else:
        try:
            files = [f.strip() for f in files.strip().split(',')]
        except:
            logging.error('Please provide a comma-separated names of at least 2 inputs (column-like files).')
    
    #-- check if matching_cols arg has correct length
    matching_cols = [str(c).strip() for c in matching_cols.strip().split(',')]
    l = len(matching_cols)
    if l == 1:
        col = matching_cols[0]
        matching_cols = [col for i in files]
    elif l != len(files):
        logging.error('Wrong number of indexes for matching columns. You provided ' + str(l) + 
                      'indexes while correct number is 1 (when all inputs have the same format and column order) or ' +
                      str(len(files)) + ' (when matching columns have different indexes for different inputs).')
        sys.exit(1)

    #-- check if keep_cols arg has correct format
    if keep_cols != '':
        keep_cols = [str(c).strip().split(',') for c in keep_cols.strip().split(':')]
        l = len(keep_cols)
        if l == 1:
            cols = keep_cols[0]
            keep_cols = [cols for i in files]
        elif l != len(files):
            logging.error('Wrong number of column ranges to be kept from inputs. You provided ' + str(l) + 
                      'lists while correct number is 1 (when keep the same columns from all files) or ' +
                      str(len(files)) + ' (when keep different columns from each input).')
            sys.exit(1)
        
    #-- check if all inputs exist; if true, load their content
    for num, f in enumerate(files):
        if not Path(f).is_file():
            logging.error('The ' + str(f) + 'does NOT exist. Please provide the correct list of inputs.')
            sys.exit(1)
        else:
            try:
                FILES[num] = load_input_file(f)							# file1, file2, ...
                COLS[num] = [name+"_"+str(num) for name in FILES[num].columns.tolist()]		# headers in files
                FILES[num].columns = COLS[num]			# make sure headers among inputs are unique (different columns names for inputs with the same format)
            except:
                logging.error('The ' + str(f) + 'was not loaded. ')

            #-- if provided indexes of matching_cols, then find their headers
            if matching_cols[num].isnumeric():
                LABS[num] = COLS[num][int(matching_cols[num])]				# names of matching columns
            elif str(matching_cols[num])+"_"+str(num) in COLS[num]:
                LABS[num] = str(matching_cols[num])+"_"+str(num)
            else:
                COLS.pop(num, None)
                FILES.pop(num, None)
                logging.warning('The user-provided index or name of matching column (' + str(matching_cols[num]) +
                              ') does NOT exist in the corresponding input file: ' + str(f) + ': \n' +
                              str(FILES[num].columns) + '. The columns from the ' + str(f) + ' file will NOT be merged in the output..')

            #-- if provided columns to be kept, then filter dataframes
            if len(keep_cols):
                tmp_cols = keep_cols[num]
                KEEP = [LABS[num]]
                for n, col in enumerate(tmp_cols):
                    if col.isnumeric() and int(col) < len(COLS[num]):
                        KEEP.append(COLS[num][int(col)])
                    elif str(col)+"_"+str(num) in COLS[num]:
                        KEEP.append(str(col)+"_"+str(num))
                    else:
                        col = col.split('-')
                        if len(col) == 2 and col[0].isnumeric() and col[1].isnumeric():
                            for each in range(int(col[0]), int(col[1]) + 1):
                                if each < len(COLS[num]):
                                    KEEP.append(COLS[num][each])
                        else:
                            logging.warning('The provided columns: ' + str(col) + ' expected to be kept from the ' +
                                            str(f) + ' file are incorrect and can NOT be merged into output. Please check your files.')
                try:
                    FILES[num] = FILES[num][KEEP]
                except:
                    logging.error('Selecting columns: \n' + str(KEEP) + '\n expected to be kept from ' + str(f) + ' file has failed.')
                        
###-- add all columns from file2 into file1 based on matching columns
        if num == 0:
            DF = FILES[num]
        else:
            DF = pd.merge(DF, FILES[num], left_on=[LABS[0]], right_on=LABS[num], how='outer').drop(LABS[num], axis=1).fillna(error_value)
    
#    DF.fillna(error_value)
    

###-- export output data_file
    if outfile == 'data_output':
        outfile += tag        
    if output_format == 1:
        DF.to_csv(outfile+'.csv', sep=',', encoding='utf-8')     # output in CSV format
    elif output_format == 2:					
        DF.to_excel(outfile+'.xlsx', index=False, header=True)   # output in xlsx format (Excel)
    else:
        DF.to_csv(outfile+'.csv', sep=sep, encoding='utf-8')

    for num, i in enumerate(files):
        print(num, i)


###-- add options to the argument parser to make it easier to customize and run the script from the command line
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='merge_multifiles.py',
        description="""Merge data from multiple files using matching column.\n 
                       Requirements: python3, pandas, openpyxl, csv""",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=''
    )
    parser.add_argument(
        '-i', '--data-file-1',
        help='[string] input multi-col file',
        metavar='files',
        dest='files',
        required=True
    )
    parser.add_argument(
        '-c', '--matching-columns',
        help='list of matching columns in the input files, e.g., 1 (when all inputs in the same format) or 0,5 or label1,label2 (when inputs are different) \ncol index starting from 0 [int] or headers',
        metavar='mcols',
        dest='mcols',
        required=True
    )
    parser.add_argument(
        '-k', '--keep-columns',
        help='list of columns to be kept, e.g., 0,5 or label1,label2 (when all inputs in the same format) or 0,5:8 or label1,label2;label3 (when inputs are different) \ncol index starting from 0 [int] or headers',
        metavar='kcols',
        dest='kcols',
        default=''
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
        print("\nUSAGE:\n	e.g., python3 merge_multifiles.py -i input_files -c 1,5 \n")
        sys.exit(1)

    args = parser.parse_args()
    merge_multifiles(args.files, args.mcols, args.kcols, args.error, args.outfile, args.format)
