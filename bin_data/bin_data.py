# -*- coding: utf-8 -*-
import os			# to manage paths
import sys			# to manage inline arguments
import argparse			# to convert python script into program with options
import logging                  # to provide verbosity level
import pandas as pd		# to easily parse json object and filter out data; require installation with conda or pip
import numpy as np              # to parse advanced numerical data structures; require installation
import csv			# to read any column-like text file
import re                       # to use regular expressions, e.g., to extract numerical part of a string for sorting


LABELS = {}
STATS = {}


def natural_sort(s, _re=re.compile(r'(\d+)')):
    return [int(t) if i & 1 else t.lower() for i, t in enumerate(_re.split(s))]


def get_delimiter(filename: str) -> str:
    try:
        with open(filename, 'r') as csvfile:
            delimiter = str(csv.Sniffer().sniff(csvfile.read()).delimiter)
        return delimiter
    except:
        logging.error('Identifying data delimiter has failed!')
    

def identify_header(filename, sep, n=10, th=0.9):
    try:
        df1 = pd.read_csv(filename, sep=sep, header='infer', nrows=n)
        df2 = pd.read_csv(filename, sep=sep, header=None, nrows=n)
        sim = (df1.dtypes.values == df2.dtypes.values).mean()
        cols = len(df1.columns)
        return ['infer', df1.columns] if sim < th else [None, cols]
    except:
        logging.error('Identifying data header has failed!')

def save_chunks(df, this_label):
    path = os.path.join(os.getcwd(),'CHUNKS')
    try:
        os.makedirs(path, exist_ok=True)
        outfile = 'chunk_' + str(this_label) + '.csv'
        df.to_csv(os.path.join(path,outfile), index=False, mode='w', header=not os.path.exists(outfile))
        logging.info("-- the dataframe saved into the file: "+str(outfile))
    except:
        logging.error("-- the dataframe could NOT be saved into the file: "+str(outfile))


def resize_data(label_df, names, labels, ranges, stat, n_split, split_type, decimal):
    """Resize data (by mean or sum) for a given label using split of n-bins or n-long step or values range"""

    lr = [names[labels], names[ranges]]		# labels and ranges
    nd = [i for i in names if not i in lr] 	# numerical data

    if split_type == 'value':
        logging.info("-- slice data with constant increment of values in ranges column...")
        lab = label_df[lr[0]].iloc[0]
        mini = label_df[lr[1]].min()
        maxi = label_df[lr[1]].max()
        groups = label_df.groupby(pd.cut(label_df[lr[1]], np.arange(mini, maxi+n_split, n_split)))
        counts = groups[lr[0]].count().reset_index(drop=True)
        if stat == 'ave':
            logging.info("-- aggregate data by averaging columns over the slice...")
            bini = groups.mean().drop(lr[1], axis=1).reset_index()
        else:
            logging.info("-- aggregate data by summing columns over the slice...")
            bini = groups.sum().drop(lr[1], axis=1).reset_index()            
        bini['count'] = counts
        bini.insert(0, lr[0], lab)
        bini[nd] = bini[nd].round(decimal)
        bini[lr[1]] = bini[lr[1]].astype(str).str.replace(', ', '-', regex=False).str.replace('(','', regex=False).str.replace(']','', regex=False)
        return bini

    else:
        step = int(n_split)
        if split_type == 'bin':
            step = int(np.ceil(len(label_df)/n_split))
            logging.info("-- slice data with constant number of "+str(step)+" slices...")
        else:
            logging.info("-- slice data with constant number of "+str(step)+" rows in a slice...")
        try:
            logging.info("-- concatenate ranges...")
            maxi = label_df[lr[1]].max()
            label_df['shift'] = label_df[lr[1]].shift(-step+1).fillna(maxi)
            label_df['shift'] = label_df[lr[1]].astype(str) + '-' + label_df['shift'].astype(type(maxi)).astype(str)
            indi = label_df[[lr[0], 'shift']].iloc[::step, :] 
            indi.rename({'shift': lr[1]}, axis=1, inplace=True)
            if stat == 'ave':
                logging.info("-- aggregate data by averaging columns over the slice...")
                bini = label_df.loc[:,nd].groupby(label_df.index // step).mean()
            else:
                logging.info("-- aggregate data by summing columns over the slice...")
                bini = label_df.loc[:,nd].groupby(label_df.index // step).sum()
        except:
            logging.error("ERROR: Aggregating data has failed!")

        if len(indi) > 0 and len(bini) > 0:
            try:
                final = pd.concat((indi.reset_index(drop=True), bini.reset_index(drop=True)), axis=1)
                final[nd] = final[nd].round(decimal)
                return final
            except:
                logging.error('ERROR: Aggregating data has failed!')
                sys.exit(1)


def concat_label_chunks(this_label, all_data, ranges, chunk_save):

    label_df = pd.concat(all_data)  # merge chunks with data for a given label
    mem2 = round(label_df.memory_usage(deep=True).sum()/1024/1024,2)
    STATS[this_label] = [len(label_df), str(mem2)+'MB']
    logging.info("-- the dataframe size is: "+str(len(label_df))+' rows and '+str(mem2)+'MB')

    # sort dataframe by ascending values in ranges column
    try:
        label_df = label_df.sort_values(by=ranges, ascending=True)
        logging.info("-- the dataframe is sort ascending by ranges column: "+str(ranges))
    except:
        logging.warning("-- kept original order since ranges column was not specified!")
                    
    # save data chunks in the ./CHUNKS directory
    if chunk_save == 'true':
        save_chunks(label_df, this_label)

    return label_df


def create_data_chunks(input_file, labels, ranges, llist, names, chunk_size, chunk_save, stat, split_type, n_split, decimal, output):
    """Split Big Data into the memory-affordable chunks and resize content by mean or sum of customized split size (n-bins or n-long step)."""

    all_bini = []	# list of all resized df grouped by labels
    if llist != '':
        if os.path.isfile(llist):
            llist = [line.strip() for line in open(llist, 'r').readlines()]
        elif isinstance(llist, str):
            llist = llist.strip().split(',')
        
    # process chunks from the directory
    if os.path.isdir(input_file):
        logging.info('0. Process chunks from the directory...')
        files = os.listdir(input_file)
        files = sorted(files, key=natural_sort)
        if llist != '':
            files = ['chunk_'+str(x)+'.csv' for x in llist if 'chunk_'+str(x)+'.csv' in files]
        if len(files):
            for num,ifile in enumerate(files):
                if ifile.startswith('chunk_'):
                    logging.info('1. Loading the '+str(num)+'th file: '+str(ifile)+'...')
                    label_df = pd.read_csv(os.path.join(input_file, ifile))
                    names = list(label_df.columns)
                    logging.info('2. Resizing data using '+str(stat)+' on the '+str(n_split)+' '+str(split_type)+'s...')
                    try:
                        bini = resize_data(label_df, names, labels, ranges, stat, n_split, split_type, decimal)   # bin data for a given label
                    except:
                        logging.error('Error: To aggregate data you need to specify column indexes with labels [-l] and ranges [-r].')
                        sys.exit(1)
                    logging.info('3. Appending resized dataframe for '+str(num)+'th label...')
                    all_bini.append(bini)
        else:
            logging.error('There are NO chunks for the labels in the list! '+str(llist))
        
    # create and process chunks from raw file
    elif os.path.isfile(input_file):
        logging.info('0. Process raw input file...')

        # Specify data delimiter
        chunk = pd.read_csv(input_file, nrows=100)		         # get data sample
        chunk.to_csv('chunk.csv', index=False)
        sep = get_delimiter('chunk.csv')                             
        logging.info('--The detected data separator is: _'+str(sep)+'_')

        # Specify data header (if it exists) 
        header = None
        head = identify_header('chunk.csv', sep=sep)                    
        if names != None and len(names) == head[1]:
            if head[0] == 'infer':
                header = 0
        else:
            if head[0] == 'infer':
                header = 0
                names = head[1]
            else:
                names = ['val-'+str(i) for i in range(head[1])]
                try:
                    names[ranges] = 'position'
                except:
                    pass
                try:
                    names[labels] = 'label'
                except:
                    pass
        logging.info('--The assigned data header is: '+str(names))

        chunk_id = 1
        # Optimize memory use when chunk size is NOT user-provided        
        if chunk_size == 0:                                       # optimize memory use to 250MB/chunk
            chunk = pd.read_csv(input_file, nrows=1000, sep=sep)     # read col-separated data sample
            mem = round(chunk.memory_usage(deep=True).sum()/1024,0)  # estimate mem [kB] for col-separated data
            chunk_size = round(250000/mem)*1000
            logging.info('--The optimized data chunk contains: '+str(chunk_size)+' rows of '+str(mem)+'kB in total.')
        else:
            logging.info('--You requested data chunks of '+str(chunk_size)+' rows each.')

        # Parse data
        all_data = []						     # list of all matching df chunks
        label_df = pd.DataFrame()                                    # creates a new empty dataframe for each label
        this_label = ''
        ## load data from chunks and merge them by labels
        for chunk in pd.read_csv(input_file, chunksize=chunk_size, sep=sep, index_col=None, header=header, names=names):
            logging.info("1. Loading chunk: "+str(chunk_id)+' ...')            
            for lab in list(chunk[names[labels]].unique()):
                ### collect data for raw file stats (list of chunks for a given label)
                if llist != '' and lab not in llist:
                    continue
                elif lab not in LABELS:
                    LABELS[lab] = [chunk_id]
                elif chunk_id not in LABELS[lab]:
                    LABELS[lab].append(chunk_id)
                
                ### collect data for a given label (merge chunks by label)
                if this_label == '':
                    this_label = lab
                    logging.info("2. Creating dataframe for a label: "+str(this_label)+'...')
                    all_data.append(chunk.loc[chunk[names[labels]] == this_label])
                elif this_label == lab:		# append all label-matching rows from the chunk
                    all_data.append(chunk.loc[chunk[names[labels]] == this_label])
                else:                               # resize data for this_label and begin cycle for next label
                    try:
                         r = names[ranges]
                    except:
                         r = ''
                    label_df = concat_label_chunks(this_label, all_data, r, chunk_save)
    
                    # bin data for a given label
                    try:
                        logging.info("3. Resizing dataframe for a label: "+str(this_label)+'...')
                        bini = resize_data(label_df, names, labels, ranges, stat, n_split, split_type, decimal)
                        logging.info("-- a new dataframe size is: "+str(len(bini))+' rows, resized by '+str(stat)+' on '+str(n_split)+' '+str(split_type)+'s')
                        all_bini.append(bini)
                    except:
                        logging.error("ERROR: Aggregating data over slices has failed!")

                    # begin cycle for next label
                    this_label = lab
                    logging.info("2. Creating dataframe for a label: "+str(this_label)+'...')
                    all_data = []
                    all_data.append(chunk.loc[chunk[names[labels]] == this_label])
            chunk_id+=1
        # bin data for the last label
        label_df = concat_label_chunks(this_label, all_data, r, chunk_save)
        logging.info("3. Resizing dataframe for a label: "+str(this_label)+'...')
        bini = resize_data(label_df, names, labels, ranges, stat, n_split, split_type, decimal)
        logging.info("-- a new dataframe size is: "+str(len(bini))+' rows, resized by '+str(stat)+' on '+str(n_split)+' '+str(split_type)+'s')
        all_bini.append(bini)
        
        try:
            logging.info("Saving statistics of a raw file into the label_in_chunks.txt ...")
            f = open("label_in_chunks.txt", "w")
            for lab in LABELS.keys():
                try:
                    f.write(str(lab)+","+str(STATS[lab][0])+","+str(STATS[lab][1])+","+str(LABELS[lab])+'\n')
                except:
                    logging.error('The '+str(lab)+' label-related error occured!')
                    continue
            f.close()
        except:
            pass
        
        if os.path.isfile('chunk.csv'):
            os.remove('chunk.csv')

    else:
        logging.critical('The input provided is not a file or directory with chunks.')
        sys.exit(1)

    # save aggregated output
    if len(all_bini):
        if not output.endswith('.csv'):
            output = output + '.csv'
        logging.info("4. Saving resized data into the "+str(output)+" file ...")
        pd.concat(all_bini).to_csv(output, index=False, mode='w', header=not os.path.exists(output))


###-- add options to the argument parser to make it easier to customize and run the script from the command line
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='bin_data.py',
        description="""Split large file into chunks and resize data by stats on slices.\n 
                       Requirements: python3, pandas, csv""",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=''
    )
    parser.add_argument(
        '-i', '--data-source',
        help='[string] input multi-col file or directory with data chunks',
        metavar='input',
        dest='input',
        type=str,
        required=True
    )
    parser.add_argument(
        '-l', '--labels-col',
        help='[int] index of column with labels used to chunk data',
        metavar='label',
        dest='label',
        type=int,
        required=True
    )
    parser.add_argument(
        '-r', '--ranges-col',
        help='[int] index of column with ranges used to slice data',
        metavar='range',
        dest='range',
        type=int,
        required=True
    )
    parser.add_argument(
        '-ll', '--label-list',
        help='provide custom list of labels to be extracted; default='' means all to be extracted',
        metavar='llist',
        dest='llist',
        default=''
    )
    parser.add_argument(
        '-hd', '--header',
        help='provide custom list of columns names (header)',
        metavar='header',
        dest='header',
        default=[],
        type=list
    )
    parser.add_argument(
        '-ch', '--chunk-size',
        help='provide custom size of chunks (number of rows)',
        metavar='chunks',
        dest='chunks',
        default=0,
        type=int
    )    
    parser.add_argument(
        '-s', '--chunk-save',
        help='saves data into chunked files [default: on]',
        choices=['true', 'false'],
        default='true',
        dest='save'
    )
    parser.add_argument(
         '-c', '--calc-stats', 
         help="select resizing opeartion: ave (mean) or sum",
         choices=['ave', 'sum'],
         default='ave', 
         dest='calc'         
    )
    parser.add_argument(
         '-t', '--slice-type', 
         help="select type of slicing: step (number of rows in a slice) or bin (number of slices) or value (value increment in ranges col)",
         choices=['step', 'bin', 'value'],
         default='step',
         dest='type'         
    )
    parser.add_argument(
         '-n', '--slice-size', 
         help="select size of slicing",
         type=float,
         default=100,
         metavar='slice',
         dest='slice'         
    )
    parser.add_argument(
         '-d', '--decimal-out', 
         help="provide decimal places for numerical outputs",
         type=int,
         default=2,
         metavar='dec',
         dest='dec'         
    )
    parser.add_argument(
         '-o', '--output', 
         help="provide custom output filename",
         type=str,
         default='output_data',
         metavar='out',
         dest='out'         
    )
    parser.add_argument(
         '-v', '--verbose', 
         const=1, 
         default=0, 
         type=int, 
         nargs="?",
         help="increase verbosity: 0 = warnings, 1 = info, 2 = rich info"
    )



###-- print example of usage and help message when script is run without required arguments
    if len(sys.argv) < 3:
        parser.print_help()
        print("\nUSAGE:\n")
        print("e.g., minimal required inputs:\n 	python3 bin_data.py -i input_file -l 0 -r 1 \n")
        print("e.g., using raw input file:\n 	python3 bin_data.py -i hybrid.depth -l 0 -r 1 -t 'step' -n 1000 -s True -v 1 \n")
        print("e.g., using directory of chunks:\n 	python3 bin_data.py -i CHUNKS/ -l 0 -r 1 -t 'value' -n 0.15 -s False -v 0 \n")
        print("e.g., using default settings:\n 	python3 bin_data.py -i {path} -l {int} -r {int} -ll None -hd None -ch 0 -s True -c 'ave' -t 'step' -n 100 -d 2 -o 'output_data' -v 0 \n")
        sys.exit(1)

    args = parser.parse_args()
    logger = logging.getLogger()
    if args.verbose == 0:
        logger.setLevel(logging.WARN) 
    elif args.verbose == 1:
        logger.setLevel(logging.INFO) 
    elif args.verbose == 2:
        logger.setLevel(logging.DEBUG) 
    
    create_data_chunks(args.input, args.label, args.range, args.llist, args.header, args.chunks, args.save, args.calc, args.type, args.slice, args.dec, args.out)
