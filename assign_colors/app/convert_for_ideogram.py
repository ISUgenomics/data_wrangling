# -*- coding: utf-8 -*-
import os                       # to manage paths
import sys                      # to manage inline arguments
import argparse                 # to convert python script into program with options
import pandas as pd             # to easily parse json object and filter out data; require installation with conda or pip
import numpy as np              # to parse advanced numerical data structures; require installation
import re                       # to use regular expressions
import json                     # to save data into json format


COLORS_9 = {0: 'gneg', 1: 'gpos25', 2: 'gpos33', 3: 'gpos50', 4: 'gpos66', 5: 'gpos75', 6: 'gpos100', 7: 'acen', 8: 'gvar'}
COLORS_3 = {0: 'gpos25', 1: 'gpos50', 2: 'gpos100'}


def extract_digits(txt):
    return '-'.join([s for s in re.findall(r'\d+', txt) if s.isdigit()])


def convert_for_ideogram(input_file, labels, ranges, arms, bands, values, measure, mtype, step, cs):

    ideo = {}
    merge = {'chrBands':[]}
    data_df = pd.read_csv(input_file)
    
    keys = list(data_df.columns)
    to_drop = [keys[labels], keys[ranges], "count"]
    try:
        to_drop.append(keys[arms])
        to_drop.append(keys[bands])
    except:
        print('')
        
    if values == '':
        values = [x for x in keys if x not in to_drop]
    else:
       values = values.split(',')
       values = [data_df.columns[int(i)] for i in values]
       to_drop = [x for x in keys if x not in values]
    to_drop.remove(keys[labels])
    for val in values:
        ideo[val] = {'chrBands':[]}

    ### - [list] per treat/individual (all labels in the batch for statistics)
    values_df = data_df[values]
    mini = values_df.iloc[:,:].min().astype(float).round(3).to_dict()		# minimum
    maxi = values_df.iloc[:,:].max().astype(float).round(3).to_dict()		# maximum
    mean = values_df.iloc[:,:].mean().astype(float).round(3).to_dict()		# mean
    medi = values_df.iloc[:,:].median().astype(float).round(3).to_dict()	# median
    std = values_df.iloc[:,:].std().astype(float).round(3).to_dict()		# standard deviation

    tmp_format = ' '.join(['{:>10}' for i in values])
    print("#-OVARALL STATS:")
    print(" KEYS:", tmp_format.format(*list(mean.keys())))
    print(" MINI:", tmp_format.format(*list(mini.values())))
    print(" MAXI:", tmp_format.format(*list(maxi.values())))
    print(" MEAN:", tmp_format.format(*list(mean.values())))
    print(" MEDI:", tmp_format.format(*list(medi.values())))
    print(" STDV:", tmp_format.format(*list(std.values())))

    ### - [matrix] per treat/individual AND groups/labels (separate statistics for each label)
    sorter = data_df[keys[labels]].unique().tolist()			# ordered list of unique labels
    dummy = pd.Series(sorter, name = keys[labels]).to_frame()
    stats_df = data_df.drop(to_drop, axis=1).groupby(keys[labels])
    pd.set_option('display.max_rows', len(sorter), 'display.max_columns', len(data_df.columns), 'display.width', 1000, 'display.precision', 3)

    mini_val = min(list(mini.values()))
    mini_tab = pd.merge(dummy, stats_df.min(), on = keys[labels], how = 'left')
    print("\n#-MINI IN GROUPS = ", mini_val, "\n", mini_tab)
    mini_tab.set_index('label', inplace=True)
    
    maxi_val = max(list(maxi.values()))
    maxi_tab = pd.merge(dummy, stats_df.max(), on = keys[labels], how = 'left')
    print("\n#-MAXI IN GROUPS = ", maxi_val, "\n", maxi_tab)
    maxi_tab.set_index('label', inplace=True)
    
    mean_val = np.mean(list(mean.values()))
    mean_tab = pd.merge(dummy, stats_df.mean(), on = keys[labels], how = 'left')
    print("\n#-MEAN IN GROUPS = ", mean_val, "\n", mean_tab)
    mean_tab.set_index('label', inplace=True)
    
    medi_tab = pd.merge(dummy, stats_df.median(), on = keys[labels], how = 'left')
    print("\n#-MEDI IN GROUPS:\n", medi_tab)
    
    stdv_tab = pd.merge(dummy, stats_df.std(), on = keys[labels], how = 'left')
    print("\n#-STDV IN GROUPS:\n", stdv_tab)
    stdv_tab.set_index('label', inplace=True)

    # PREPARE VALUE-TO-COLOR MAPPING MATRIX
    color_dict = {}
    CS = COLORS_3
    if step != "std":
        intervals = [float(x) for x in str(step).split(",")]
        if len(intervals) > 3:
            CS = COLORS_9
    if len(cs) > 0:
        CS = {num : str(x) for num,x in enumerate(cs.split(","))}


    ### - color scale related to reference value for each group/label/row [l] (mixed individuals for given label)
    if mtype == "row":
        for j in sorter:			# iterate labels/chromosomes/rows
            colors = {}
            color_ref = str(j)
            stdv_l = stdv_tab.loc[[j]].fillna(0).mean(axis=1, numeric_only=True)[0]
            maxi_l = maxi_tab.loc[[j]].fillna(0).max(axis=1)[0]
            medi_l = medi_tab[medi_tab['label'] == j].fillna(0).mean(axis=1, numeric_only=True).values[0]
            metric = mean_tab.loc[[j]].fillna(0).mean(axis=1, numeric_only=True)[0]	# default mean as the middle of the colorscale
            if measure == "median":							# median as the center of the colorscale
                metric = medi_l
            elif measure == "max":							# half of the maximum as the center of the colorscale
                metric = maxi_l/2
            if step == 'std':
                intervals = [metric - stdv_l, metric + stdv_l, maxi_l]
            else:
                intervals = list(np.array(intervals) * metric)

            for num, i in enumerate(intervals):
                colors[i] = CS[num]
            color_dict[str(j)] = colors

    else:
        for val in values:			# iterate treats/individuals/columns
            colors = {}

            if mtype == "glob":
        ### - color scale related to maximum value among all observations
                metric = mean_val
                if measure == "median":			# median as the center of the colorscale
                    metric = medi_val
                elif measure == "max":			# half of the maximum as the center of the colorscale
                    metric = maxi_val/2
                if step == 'std':
                    intervals = [metric - std_val, metric + std_val, maxi_val]
                else:
                    intervals = list(np.array(intervals) * metric)

                for num, i in enumerate(intervals):
                    colors[i] = CS[num]
                color_dict[val] = colors			# [g] val
                
            elif mtype == "column":
            ### - color scale related to reference value for each treat/individual [i]
                metric = mean[val]
                if measure == "median":			# median as the center of the colorscale
                    metric = medi[val]
                elif measure == "max":			# half of the maximum as the center of the colorscale
                    metric = maxi[val]/2
                if step == 'std':
                    intervals = [metric - std[val], metric + std[val], maxi[val]]
                else:
                    intervals = list(np.array(intervals) * metric)

                for num, i in enumerate(intervals):
                    colors[i] = CS[num]
                color_dict[val] = colors			# [i] val

            elif mtype == "cell":
            ### - color scale related to mean value for each group (label) in each treat/individual [u] (unique labels and individuals)
                for j in sorter:								
                    colors = {}
                    color_ref = str(j)+"-"+str(val)		# individual x label 
                    metric = mean_tab.loc[j, val]
                    if measure == "median":			# median as the center of the colorscale
                        metric = medi_tab.loc[j, val]
                    elif measure == "max":			# half of the maximum as the center of the colorscale
                        metric = maxi_tab.loc[j, val]/2
                    if step == 'std':
                        intervals = [metric - stdv_tab.loc[j,val], metric + stdv_tab.loc[j,val], maxi_tab.loc[j,val]]
                    else:
                        intervals = list(np.array(intervals) * metric)

                    for num, i in enumerate(intervals):
                        colors[i] = CS[num]
                    color_dict[color_ref] = colors		# [u] label-val


    
    # CREATE DATA STRUCTURE FOR IDEOGRAM JS
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
            color_ref = val				# [g] or [i]
            if mtype == "row":
                color_ref = str(row.label)		# [l]
            elif mtype == "cell":
                color_ref = str(row.label)+"-"+str(val)	# [u]
            color = 'gvar'
            colors = color_dict[color_ref]
            for n, est in enumerate(colors.keys()):
                if row[val] <= est:
                    color = colors[est]
                    break
            
            string = str(idx)+' '+str(arm)+' '+str(band)+' '+str(start)+' '+str(end)+' '+str(start)+' '+str(end)+' '+str(color)
            ideo[val]['chrBands'].append(string)
            
            string2 = str(idx)+'-i'+str(val.split('-')[1])+' '+str(arm)+' '+str(band)+' '+str(start)+' '+str(end)+' '+str(start)+' '+str(end)+' '+str(color)
            merge['chrBands'].append(string2)

    for value in ideo:
        with open('data-'+value+'.json', 'w') as f:
            json.dump(ideo[value], f)
    
    with open('merge.json', 'w') as f:
        json.dump(merge, f)
    
###-- add options to the argument parser to make it easier to customize and run the script from the command line
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='convert_for_ideogram.py',
        description="""Value-to-color mapping and data convertion to ideogram format.\n 
                       Requirements: python3, pandas, numpy""",
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
        help='[int] index of column with labels',
        metavar='label',
        dest='label',
        type=int,
        required=True
    )
    parser.add_argument(
        '-r', '--ranges-col',
        help='[int] index of column with ranges',
        metavar='range',
        dest='range',
        type=int,
        required=True
    )    
    parser.add_argument(
        '-a', '--arms-col',
        help='[int] index of column with chromosome arms annotation',
        metavar='arm',
        dest='arm',
        type=int,
        default=None
    )     
    parser.add_argument(
        '-b', '--bands-col',
        help='[int] index of column with bands annotation (names)',
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
        type=str,
        default=''
    )
    parser.add_argument(
        '-m', '--measure', 
        help="select type of color reference: 'max' (maximum value) or 'mean' or 'median'",
        choices=['max', 'mean', 'median'],
        default='mean',
        dest='measure'         
    )
    parser.add_argument(
        '-t', '--measure-type', 
        help="select type of measure: 'glob' (stats over entire dataset) or 'row' (stats per data row) or 'col' (stats per data column) or 'cell' (stats per row-col pair)",
        choices=['glob', 'row', 'column', 'cell'],
        default='cell',
        dest='mtype'         
    )
    parser.add_argument(
        '-s', '--step',
        help="provide color interval: 'std' (standard deviation by default) or comma-separated list of thresholds (e.g., 0.4,0.6,1.0)",
        dest='step',
        type=str,
        default='std'
    )
    parser.add_argument(
        '-cs', '--colorscale',
        help="provide custom colorscale: comma-separated list of hex colors (e.g., #FFFFFF,#a6a6a6,#000000 set up the white-gray-black scale)",
        dest='cs',
        type=str,
        default=''
    )


###-- print example of usage and help message when script is run without required arguments
    if len(sys.argv) < 2:
        parser.print_help()
        print("\nUSAGE:\n")
        print("e.g., minimal required inputs:\n         python3 convert_for_ideogram.py -i input_file -l 0 -r 1")
        sys.exit(1)

    args = parser.parse_args()
    convert_for_ideogram(args.input, args.label, args.range, args.arm, args.band, args.vals, args.measure, args.mtype, args.step, args.cs)
