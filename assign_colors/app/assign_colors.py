# -*- coding: utf-8 -*-
import sys                      # to manage inline arguments
import argparse                 # to convert python script into program with options
import logging			# to provide verbosity level
import pandas as pd             # to easily parse json object and filter out data; require installation with conda or pip
import numpy as np              # to parse advanced numerical data structures; require installation
from colorsys import hls_to_rgb # to generate various color scales
import PIL
from PIL import Image, ImageDraw


numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
HLS = {'red': 0, 'vermilion': 0.5, 'orange': 1, 'golden': 1.5, 'yellow': 2, 
       'yellowish': 2.5, 'chartreuse': 3, 'leaf': 3.5, 'green': 4, 
       'cobalt_green': 4.5, 'emerald': 5, 'turquoise': 5.5, 'cyan': 6, 
       'cerulean': 6.5, 'azure': 7, 'blue': 7.5, 'ultramarine': 8, 
       'hyacinth': 8.5, 'violet': 9, 'purple': 9.5, 'magenta': 10, 
       'reddish_purple': 10.5, 'crimson': 11, 'carmine': 11.5}


def generate_colorscale(c=0, t='full', n=12, l=0.5, s=1.0, a=0.9, h='true', r='false'):
    """Returns dictionary of indexed colors (rgba or hex)"""
    if c == 0 :
        if t == 'full':		# rainbow color scale
            rgba_colors = [ tuple((255*np.array(hls_to_rgb(0.95 * i/(n-1), l, s))).astype(int))+(a,) for i in range(n) ]
        if t == 'grey':		# black-gray-white color scale
            rgba_colors = [ tuple((255*np.array(hls_to_rgb(0.0, i/(n-1), 0.0))).astype(int))+(a,) for i in range(n) ]
        elif t in HLS:		# shades of the selected color
            rgba_colors = [ tuple((255*np.array(hls_to_rgb(HLS[t]/12.0, i/(n-1), s))).astype(int))+(a,) for i in range(n) ]
    else:			# when t is a list
        n = len(t)
        if t[0] in HLS:	# user-provided list of colors pre-defined in the HLS dictionary, e.g., "red,purple,violet,blue,cyan"
            try:
                rgba_colors = [ tuple((255*np.array(hls_to_rgb(HLS[val]/12.0, l, s))).astype(int))+(a,) for val in t ]
            except:
                logging.error('Provided color names do NOT match the predefined list. Please select colors from: \n' + str(HLS.values()))
        else:
            try:		# user-provided list of floats in range 0-12, e.g., "0.5,1.0,3.0,6.5,10.0"
                vals = [s for s in t if s.isdigit()]
                rgba_colors = [ tuple((255*np.array(hls_to_rgb(val/12.0, l, s))).astype(int))+(a,) for val in vals ]
            except:
                print("ERROR: user-provided values are not a list of floats in range 0-12")

    if r == 'true':
        rgba_colors.reverse()
    if h == 'true':	# HEX colors
        colors = [ '#{:02x}{:02x}{:02x}'.format(*color) for color in rgba_colors ]
    else:		# RGBA colors
        colors = ['rgba'+str(color) for color in rgba_colors]

    return { n : i for n, i in enumerate(colors) }, rgba_colors


def assign_colors(cs='grey', cs_params="3,0.5,1.0,0.9,true,false", input_file='', labels='', values='', measure='mean', mtype='cell', step='std'):
    """Generate color scale and perform value-to-color mapping"""

    # PREPARE COLOR SCALE (using cs argument)
    CS = []
    rgba = []
    csp = cs_params.strip().replace(' ', '').split(',')
    
    if input_file != '' and  step != "std":
        intervals = [float(x) for x in str(step).split(",")]
        l = len(intervals)
        if l > 3:
            csp[0] = l
    try:
        tmp_cs = cs.strip().replace(' ', '').split(',')
        if len(tmp_cs) > 1:
            if tmp_cs[0].startswith('#') or tmp_cs[0].startswith('rgb'):	# ready-made user-provided color scale
                CS = {num : color for num,color in tmp_cs}
            else:								# list of standard colors or equivalent floats
                CS, rgba = generate_colorscale(1, tmp_cs, len(tmp_cs), float(csp[1]), float(csp[2]), float(csp[3]), str(csp[4]), str(csp[5]))
        else:									# automatically generated colorscale
            CS, rgba = generate_colorscale(0, tmp_cs[0], int(csp[0]), float(csp[1]), float(csp[2]), float(csp[3]), str(csp[4]), str(csp[5]))
    except:
        logging.error('Creating color scale has failed!')

    if len(rgba):
        n = len(rgba)
        w = 160					# width of a single color on the color scale
        img=Image.new("RGBA", ((n*w)+20, 160),(255,255,255))
        draw = ImageDraw.Draw(img)
        for num,i in enumerate(rgba):
            j = list(i)
            j[3] = int(i[3] * 255)		# convert color alpha to 1-255 range
            p1 = ((w*num)+10,10)
            shape = [p1, (p1[0]+w,150)]		# [(x0,y0),(x1,y1)]
            draw.rectangle(shape, fill=tuple(j), outline="black")
        img.save("cs.png")    

    print("COLOR SCALE: " + str(list(CS.values())))
    if input_file == '':
        sys.exit(1)


    # LOAD INPUT DATA
    data_df = pd.read_csv(input_file)
    keys = list(data_df.columns)

    if values == '':
        values = list(data_df.select_dtypes(include=numerics).columns)
    else:
       values = values.split(',')
       values = [data_df.columns[int(i)] for i in values]
    to_drop = [x for x in keys if x not in values]
    to_drop.remove(keys[labels])

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

    
    # CREATE OUTPUT DATA STRUCTURE
    f = open("colors.csv", "a")
    p = ''
    if len(to_drop) > 0:
        p = ','.join(to_drop)+','
        
    f.write(str(keys[labels])+','+p+','.join(values)+'\n')

    for index, row in data_df.iterrows():
        string = str(row[keys[labels]]) + ','
        if len(to_drop) > 0:
            string += ','.join([str(row[k]) for k in to_drop])
        
        for num, val in enumerate(values):
            color_ref = val				# [g] or [i]
            if mtype == "row":
                color_ref = str(row.label)		# [l]
            elif mtype == "cell":
                color_ref = str(row.label)+"-"+str(val)	# [u]
            color = '#ERROR'
            colors = color_dict[color_ref]
            for n, est in enumerate(colors.keys()):
                if row[val] <= est:
                    color = colors[est]
                    break
            
            string += ','+str(color)
        f.write(string+"\n")
    f.close()

    
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
        '-cs', '--colorscale',
        help="select colorscale type: provide pre-defined keyword (e.g., 'full', 'grey') or comma-separated list of colors (learn more from the docs)",
        dest='cs',
        type=str,
        default='grey'
    )
    parser.add_argument(
        '-csp', '--colorscale-params',
        help="adjust custom colorscale: comma-separated list of 6 parameters in order (1) number of colors, (2) color lightness, (3) color saturation, (4) color transparency, (5) whether to convert colors to HEX notation, (6) reverse color scale order",
        dest='csp',
        type=str,
        default="3,0.5,1.0,0.9,true,false"
    )
    parser.add_argument(
        '-i', '--data-source',
        help='[string] input multi-col file',
        metavar='input',
        dest='input',
        default=''
    )
    parser.add_argument(
        '-l', '--labels-col',
        help='[int] index of column with labels',
        metavar='label',
        dest='label',
        type=int
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


###-- print example of usage and help message when script is run without required arguments
    if len(sys.argv) < 2:
        parser.print_help()
        print("\nUSAGE:\n")
        print("e.g., minimal required inputs:\n         python3 assign_colors.py")
        print("e.g., create custom color scale only:\n         python3 assign_colors.py -cs 'red' -csp '9,0.5,1.0,0.9,true'")
        print("e.g., value-to-color mapping with the default grey scale:\n         python3 assign_colors.py -i input_file.csv -l 0")

    args = parser.parse_args()
    assign_colors(args.cs, args.csp, args.input, args.label, args.vals, args.measure, args.mtype, args.step)
