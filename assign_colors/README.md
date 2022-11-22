# assign_colors.py app (python)

## Overview

The **assign_colors** applications are written in Python3 and employ  efficient libraries [pandas and numpy] for operating on a complex data structure. The application **assigns colors** to value ranges/intervals. There are various variants of value-to-color mapping possible to set up by a combination of available options.


Value-to-color mapping facilitates:
- meaningful visualization of the results
- detecting regions/ranges enriched or depleted by the feature


## Algorithm


## Requirements


## Options of ***convert_to_ideogram.py***

help & info arguments:
```
  -h,         --help                    # show full help message and exit
```

required arguments:
```
-i input,     --data-source input       # [string] input multi-col text file
-l label,     --labels-col label        # [int]    index of column with labels
-r range,     --ranges-col range        # [int]    index of column with ranges
```

optional arguments:
```
-a arm, --arms-col arm                  # [int]    index of column with chromosome arms annotation
-b band, --bands-col band               # [int]    index of column with bands annotation (names)
-v vals, --values-col vals              # [string] comma-separated list of indices of numerical columns to have color assigned
-m type, --measure type                 # {max,mean,median} select type of measure for the colorscale  reference:
                                          - 'max' (half of the maximum value is the center of the colorscale) or
                                          - 'mean' (mean as the center of the colorscale) or
                                          - 'median' (meadian as the center of the colorscale)
-t type, --measure-type type            # {glob,row,column,cell} select type of measure:
                                          - 'glob' (stats over entire dataset) or
                                          - 'row' (stats per data row) or
                                          - 'column' (stats per data column) or
                                          - 'cell' (stats per row-col pair)
-s STEP, --step STEP                    # [string] provide color interval:
                                          - 'std' (standard deviation by default) or
                                          - comma-separated list of thresholds (e.g., 0.4,0.6,1.0)
-cs CS, --colorscale CS                 # [string] comma-separated list of HEX colors; do NOT use for ideogram-JS visualization; works with ideogram-plotly web app
                                                   (e.g., #FFFFFF,#a6a6a6,#000000 set up the white-gray-black scale)


```

*defaults for optional arguments:*
```
-a None                  # means: all chromosomes arms are considered as 'p'
-b None                  # means: names of the bands are created automatically using arm type, chromosome index, and numerical band idenfifier
-v None                  # means: all columns with numerical values (except columns used with other options) will be mapped to colors
-m 'mean'                # means: the mean value will be used as a center of the color scale
-t 'cell'                # means: the measure will be calculated for each row x column pair in the matrix (e.g., chromosome x individual)
-s 'std'                 # means: standard deviation (std) determines the color intervals, i.e., light gray below [measure - std]  and dark gray above [measure + std]
-cs ''                   # means: the default 3-colors cale (lightgray-gray-black) will be used
```

## Example usage

```
python3 convert_for_ideogram.py -i input -l label -r range
                   [-a arm_col] [-b band_col]
                   [-v cols_for_mapping]
                   [-m {max,mean,median}] [-t {glob,row,column,cell}] [-s intervals]
                   [-h]
```

*^ arguments provided in square brackets [] are optional*


* **example usage with minimal required options:**

preview of the `input_file.csv`
```
label,position,val-2,val-3,val-4,val-5,val-6,val-7,val-8,val-9,count
HiC_scaffold_1,982.0-10982.0,0.591,0.567,0.048,0.0,0.38,0.822,0.074,0.359,1373
HiC_scaffold_1,10982.0-20982.0,0.803,0.642,0.238,0.326,0.895,1.057,0.0,0.456,2025
HiC_scaffold_1,20982.0-30982.0,0.107,0.0,0.0,0.052,0.507,0.378,0.0,0.085,672
HiC_scaffold_1,30982.0-40982.0,0.471,0.0,0.417,0.0,0.206,0.007,0.0,0.0,427
HiC_scaffold_1,40982.0-50982.0,0.865,0.697,0.152,0.228,0.41,1.276,0.151,1.03,1279
...
```
run in the terminal:
```
python3 convert_for_ideogram.py -i input_file.csv -l 0 -r 1
```
equal using all default options:
```
python3 convert_for_ideogram.py -i input_file.csv -l 0 -r 1 -a None -b None -v None -m 'mean' -t 'cell' -s 'std' -cs ''
```

*The example parses the single text-like input_file, where the 'label-column' (e.g., chromosome ids) has index 0 and the 'ranges-column' (e.g., ranges of positions along the chromosome) has index 1. The 'p' arm will be assigned by default because no column with arm annotations is specified. No column with band annotations is provided, so the bands' identifiers will be created automatically. All numerical columns will be mapped into colors (except the 'count' column, if it exists). For each unique pair of row x column (e.g., chromosome x individual) the mean value will be used as the center of the 3-color scale [light gray, gray, dark gray]. The value-to-color mapping thresholds will depend on the standard deviation.*

The automatically saved output includes N + 1 JSON files, where N denotes number of [numerical] columns that were mapped to colors, and the +1 contains all the merged results (to be displayed on a single ideogram). These files are ready-made inputs for the ideogram (JS) visualization application, available to run interactively in the jupyter-lab web interface.

`data-val-2.json` - value-to-color mapped data for the individual 2 across 10 chromosomes *(separate file for each column)*
```
{"chrBands":
  [
   "1 p p1-0 982.0 10982.0 982.0 10982.0 gpos50",
   "1 p p1-1 10982.0 20982.0 10982.0 20982.0 gpos50",
   "1 p p1-2 20982.0 30982.0 20982.0 30982.0 gpos50",
   "1 p p1-3 30982.0 40982.0 30982.0 40982.0 gpos50",
   "1 p p1-4 40982.0 50982.0 40982.0 50982.0 gpos50",
   "1 p p1-5 50982.0 60982.0 50982.0 60982.0 gpos50",
   "1 p p1-6 60982.0 70982.0 60982.0 70982.0 gpos50",
   "1 p p1-7 70982.0 80982.0 70982.0 80982.0 gpos100",
   ...
   "10 p p10-46 436.0 10436.0 436.0 10436.0 gpos25",
   "10 p p10-47 10436.0 20436.0 10436.0 20436.0 gpos50",
   "10 p p10-48 20436.0 30436.0 20436.0 30436.0 gpos25",
   "10 p p10-49 30436.0 40436.0 30436.0 40436.0 gpos50",
   "10 p p10-50 40436.0 50436.0 40436.0 50436.0 gpos100"
  ]
}
```


`merge.json` - value-to-color mapped data for all (1-8) individuals across 10 chromosomes
```
{"chrBands":
  [
   "1-i2 p p1-0 982.0 10982.0 982.0 10982.0 gpos50",
   "1-i3 p p1-0 982.0 10982.0 982.0 10982.0 gpos50",
   "1-i4 p p1-0 982.0 10982.0 982.0 10982.0 gpos25",
   "1-i5 p p1-0 982.0 10982.0 982.0 10982.0 gpos25",
   "1-i6 p p1-0 982.0 10982.0 982.0 10982.0 gpos50",
   "1-i7 p p1-0 982.0 10982.0 982.0 10982.0 gpos50",
   "1-i8 p p1-0 982.0 10982.0 982.0 10982.0 gpos50",
   "1-i9 p p1-0 982.0 10982.0 982.0 10982.0 gpos50",
   ...
   "10-i2 p p10-50 40436.0 50436.0 40436.0 50436.0 gpos100",
   "10-i3 p p10-50 40436.0 50436.0 40436.0 50436.0 gpos50",
   "10-i4 p p10-50 40436.0 50436.0 40436.0 50436.0 gpos50",
   "10-i5 p p10-50 40436.0 50436.0 40436.0 50436.0 gpos50",
   "10-i6 p p10-50 40436.0 50436.0 40436.0 50436.0 gpos50",
   "10-i7 p p10-50 40436.0 50436.0 40436.0 50436.0 gpos50",
   "10-i8 p p10-50 40436.0 50436.0 40436.0 50436.0 gpos100",
   "10-i9 p p10-50 40436.0 50436.0 40436.0 50436.0 gpos50"
  ]
}
```

In addition, the standard output is displayed on the screen (*can be redirected to the file using `> filename` as a suffix to the command*). <br>It contains all statistics:
```
#-OVARALL STATS:
 KEYS:      val-2      val-3      val-4      val-5      val-6      val-7      val-8      val-9
 MINI:      0.076        0.0        0.0        0.0        0.0        0.0        0.0        0.0
 MAXI:     35.148     26.726      5.429      4.161     24.516      43.47       5.13      6.168
 MEAN:      2.939      2.545      0.836      0.721       2.64       2.51      0.822      0.835
 MEDI:      1.159      0.962      0.426      0.353      0.944      0.994      0.258      0.251
 STDV:      5.336      4.503        1.0      0.933       4.09      6.219      1.126      1.355

 #-MINI IN GROUPS =  0.0
               label  val-2  val-3  val-4  val-5  val-6  val-7  val-8  val-9
 0   HiC_scaffold_1  0.107  0.000  0.000  0.000  0.206  0.007  0.000  0.000
 1   HiC_scaffold_2  0.417  0.768  0.142  0.000  0.608  0.327  0.039  0.213
 2   HiC_scaffold_3  0.643  0.885  0.493  0.202  0.891  0.980  0.083  0.240
 3   HiC_scaffold_4  1.849  2.601  0.547  1.021  3.253  1.890  0.482  0.588
 4   HiC_scaffold_5  0.522  0.928  0.285  0.105  0.558  0.204  0.109  0.148
 5   HiC_scaffold_6  0.486  0.146  0.117  0.040  0.251  0.412  0.000  0.035
 6   HiC_scaffold_7  0.076  0.000  0.000  0.000  0.000  0.000  0.000  0.000
 7   HiC_scaffold_8  3.874  6.496  1.576  1.318  3.908  4.366  1.827  1.184
 8   HiC_scaffold_9  1.848  2.576  0.541  0.235  2.271  1.207  0.234  0.256
 9  HiC_scaffold_10  0.772  0.751  0.135  0.000  0.117  0.000  0.242  0.000

 #-MAXI IN GROUPS =  43.47
               label   val-2   val-3  val-4  val-5   val-6   val-7  val-8  val-9
 0   HiC_scaffold_1   3.458   1.908  0.417  0.438   0.895   1.593  0.831  1.030
 1   HiC_scaffold_2  35.148  26.726  5.429  3.047  24.516  43.470  5.130  6.168
 2   HiC_scaffold_3   6.301   4.692  1.977  2.135   4.320   4.662  2.965  2.122
 3   HiC_scaffold_4   4.742   3.612  1.447  1.268   4.543   3.740  2.980  2.409
 4   HiC_scaffold_5   5.242   3.800  2.159  1.133   4.691   5.975  2.260  1.209
 5   HiC_scaffold_6   1.613   1.724  1.438  0.802   2.353   1.561  0.657  0.785
 6   HiC_scaffold_7   2.184   2.173  1.490  1.444   2.477   2.708  1.646  1.141
 7   HiC_scaffold_8   9.339  14.601  2.804  3.357  10.015   6.917  2.757  3.896
 8   HiC_scaffold_9   9.472  10.185  2.304  2.276   9.641   5.288  2.242  2.611
 9  HiC_scaffold_10   8.198   7.925  2.741  4.161   9.405   8.641  2.951  6.093

 #-MEAN IN GROUPS =  1.731
               label  val-2   val-3  val-4  val-5  val-6  val-7  val-8  val-9
 0   HiC_scaffold_1  1.024   0.630  0.217  0.177  0.499  0.772  0.193  0.290
 1   HiC_scaffold_2  8.861   6.715  1.730  1.044  6.659  9.545  1.275  1.763
 2   HiC_scaffold_3  2.216   1.881  1.054  0.775  2.321  2.269  0.950  0.917
 3   HiC_scaffold_4  3.296   3.107  0.997  1.144  3.898  2.815  1.731  1.498
 4   HiC_scaffold_5  2.307   2.188  0.746  0.488  1.929  2.075  0.831  0.622
 5   HiC_scaffold_6  1.048   0.762  0.493  0.432  1.260  0.897  0.300  0.354
 6   HiC_scaffold_7  0.564   0.535  0.414  0.357  0.528  0.544  0.251  0.159
 7   HiC_scaffold_8  6.607  10.549  2.190  2.338  6.962  5.641  2.292  2.540
 8   HiC_scaffold_9  6.447   6.728  1.494  1.475  6.529  3.810  1.427  1.653
 9  HiC_scaffold_10  4.692   2.594  1.123  1.285  4.469  2.671  1.726  1.461

 #-MEDI IN GROUPS:
               label  val-2   val-3  val-4  val-5  val-6  val-7  val-8  val-9
 0   HiC_scaffold_1  0.697   0.605  0.221  0.155  0.432  0.684  0.054  0.178
 1   HiC_scaffold_2  1.933   0.995  0.942  0.431  3.196  1.008  0.191  0.740
 2   HiC_scaffold_3  0.960   0.974  0.873  0.381  2.037  1.718  0.376  0.654
 3   HiC_scaffold_4  3.296   3.107  0.997  1.144  3.898  2.815  1.731  1.498
 4   HiC_scaffold_5  1.822   1.904  0.340  0.470  1.670  1.377  0.528  0.647
 5   HiC_scaffold_6  1.222   0.598  0.304  0.598  1.345  0.934  0.246  0.245
 6   HiC_scaffold_7  0.398   0.331  0.211  0.108  0.344  0.388  0.015  0.000
 7   HiC_scaffold_8  6.607  10.549  2.190  2.338  6.962  5.641  2.292  2.540
 8   HiC_scaffold_9  8.021   7.424  1.638  1.914  7.675  4.935  1.806  2.093
 9  HiC_scaffold_10  6.404   1.039  1.019  0.927  5.883  1.749  2.127  0.186

 #-STDV IN GROUPS:
               label   val-2   val-3  val-4  val-5   val-6   val-7  val-8  val-9
 0   HiC_scaffold_1   1.079   0.627  0.147  0.166   0.227   0.518  0.300  0.338
 1   HiC_scaffold_2  14.828  11.277  2.177  1.227  10.065  18.980  2.183  2.516
 2   HiC_scaffold_3   2.729   1.874  0.671  0.915   1.446   1.684  1.361  0.837
 3   HiC_scaffold_4   2.046   0.715  0.636  0.175   0.912   1.308  1.766  1.288
 4   HiC_scaffold_5   1.854   1.207  0.800  0.418   1.650   2.311  0.896  0.438
 5   HiC_scaffold_6   0.484   0.615  0.543  0.359   0.833   0.483  0.252  0.313
 6   HiC_scaffold_7   0.583   0.625  0.524  0.548   0.666   0.761  0.485  0.341
 7   HiC_scaffold_8   3.864   5.731  0.868  1.442   4.318   1.804  0.658  1.918
 8   HiC_scaffold_9   4.048   3.852  0.890  1.089   3.816   2.261  1.056  1.238
 9  HiC_scaffold_10   3.437   3.040  1.005  1.683   3.859   3.440  1.107  2.612
```

* **example usage of value-to-color mapping for selected [numerical] column:**

```
python3 convert_for_ideogram.py -i input_file.csv -l 0 -r 1 -v 2 -m 'median' -t 'column' -s 'std' > stats_2
```

<i>In this example, the value-to-color mapping is calculated only for the numerical column of <b>index=2</b> (i.e., the third column in the input file named 'val-2'). The standard 3-color scale is centered on the <b>median</b> of <b>column</b> (corresponding to the individual-2 across all the chromosomes). Intervals on the color scale are determined by median +/- standard deviation. The statistics from the standard output are saved to the `stats_2` file for future reference.</i>

`data-val-2.json` - ideogram input file for individual 2 only (across all chromosomes) <br>
*Note one band in chromosome 7 has `gvar` color assigned. This color is used for values that are out of the color scale range. It helps to find errors in the dataset. In this case, you can see that the input contains an empty slice/bin (0 counts) for that position range [94036 - 104036] of chromosome 7. On the ideogram with the default color scale, error bands are colored pink.*
```
{"chrBands":                                                    |       
  [                                                             |       label,position,val-2,val-3,val-4,val-5,val-6,val-7,val-8,val-9,count
   ...                                                          |       ...
   "7 p p7-37 84036.0 94036.0 84036.0 94036.0 gpos50",          |       HiC_scaffold_7,84036.0-94036.0,0.426,0.0,0.574,0.0,0.0,0.0,0.0,0.0,507
   "7 p p7-38 94036.0 104036.0 94036.0 104036.0 gvar",          |       HiC_scaffold_7,94036.0-104036.0,,,,,,,,,0
   "7 p p7-39 104036.0 114036.0 104036.0 114036.0 gpos50",      |       HiC_scaffold_7,104036.0-114036.0,2.184,2.173,1.49,1.444,2.477,2.708,1.646,1.141,723
   ...                                                          |       ...
  ]                                                             |       
}                                                               |       
```

`stats_2` - statistics from standard output saved to the file
```
#-OVARALL STATS:
 KEYS:      val-2
 MINI:      0.076
 MAXI:     35.148
 MEAN:      2.939
 MEDI:      1.159
 STDV:      5.336

 #-MINI IN GROUPS =  0.076      #-MAXI IN GROUPS =  35.148      #-MEAN IN GROUPS =  2.939       #-MEDI IN GROUPS:               #-STDV IN GROUPS:         
              label  val-2                   label   val-2                  label   val-2                   label   val-2                    label   val-2
 0   HiC_scaffold_1  0.107      0   HiC_scaffold_1   3.458      0   HiC_scaffold_1  1.024       0   HiC_scaffold_1  0.697       0   HiC_scaffold_1   1.079
 1   HiC_scaffold_2  0.417      1   HiC_scaffold_2  35.148      1   HiC_scaffold_2  8.861       1   HiC_scaffold_2  1.933       1   HiC_scaffold_2  14.828
 2   HiC_scaffold_3  0.643      2   HiC_scaffold_3   6.301      2   HiC_scaffold_3  2.216       2   HiC_scaffold_3  0.960       2   HiC_scaffold_3   2.729
 3   HiC_scaffold_4  1.849      3   HiC_scaffold_4   4.742      3   HiC_scaffold_4  3.296       3   HiC_scaffold_4  3.296       3   HiC_scaffold_4   2.046
 4   HiC_scaffold_5  0.522      4   HiC_scaffold_5   5.242      4   HiC_scaffold_5  2.307       4   HiC_scaffold_5  1.822       4   HiC_scaffold_5   1.854
 5   HiC_scaffold_6  0.486      5   HiC_scaffold_6   1.613      5   HiC_scaffold_6  1.048       5   HiC_scaffold_6  1.222       5   HiC_scaffold_6   0.484
 6   HiC_scaffold_7  0.076      6   HiC_scaffold_7   2.184      6   HiC_scaffold_7  0.564       6   HiC_scaffold_7  0.398       6   HiC_scaffold_7   0.583
 7   HiC_scaffold_8  3.874      7   HiC_scaffold_8   9.339      7   HiC_scaffold_8  6.607       7   HiC_scaffold_8  6.607       7   HiC_scaffold_8   3.864
 8   HiC_scaffold_9  1.848      8   HiC_scaffold_9   9.472      8   HiC_scaffold_9  6.447       8   HiC_scaffold_9  8.021       8   HiC_scaffold_9   4.048
 9  HiC_scaffold_10  0.772      9  HiC_scaffold_10   8.198      9  HiC_scaffold_10  4.692       9  HiC_scaffold_10  6.404       9  HiC_scaffold_10   3.437
```


* **example usage with custom value-to-color mapping intervals:**

```
python3 convert_for_ideogram.py -i input_file.csv -l 0 -r 1 -v 2,3,6,7 -m 'max' -t 'row' -s 0.25,0.5,0.75,1.0,1.25,1.5,2.0
```

<i>In this example the value-to-color mapping is calculated for several numerical columns [<b>indexes: 2, 3, 6, 7</b>] (note indexing in python starts from 0). Since we use custom schema of value intervals (with option -s) and their number is higher than 3, the built-in 9-color scale (7 gray shades + pink + purple) is set automatically. The <b>maximum</b> value in the data row is the reference for the value-to-color mapping. In this example, 'row' mapping type means that for each chromosome, we find the maximum value across individuals. The half of the maximum is used as a center of the color scale when standard deviation determines intervals (default settings). Since we provide custom intervals, remember that with 'max' measure, only half of maximum value is used. So, the multiplier 1.0 corresponds to the half-max, and 2.0 corresponds to the maximum. Note that when using the built-in 9-color scale, you can provide at most nine multipliers for value intervals.</i>

`data-val-2.json`
```
{"chrBands":
  [
   "1 p p1-0 982.0 10982.0 982.0 10982.0 gpos25",
   "1 p p1-1 10982.0 20982.0 10982.0 20982.0 gpos25",
   "1 p p1-2 20982.0 30982.0 20982.0 30982.0 gneg",
   "1 p p1-3 30982.0 40982.0 30982.0 40982.0 gpos25",
   "1 p p1-4 40982.0 50982.0 40982.0 50982.0 gpos33",
   "1 p p1-5 50982.0 60982.0 50982.0 60982.0 gneg",
   "1 p p1-6 60982.0 70982.0 60982.0 70982.0 gpos50",
   "1 p p1-7 70982.0 80982.0 70982.0 80982.0 gpos100",
   ...
  ]
}
```

`merge.json`
```
{"chrBands":
  [
   "1-i2 p p1-0 982.0 10982.0 982.0 10982.0 gpos25",
   "1-i3 p p1-0 982.0 10982.0 982.0 10982.0 gpos25",
   "1-i6 p p1-0 982.0 10982.0 982.0 10982.0 gneg",
   "1-i7 p p1-0 982.0 10982.0 982.0 10982.0 gpos25",
   ...
   "10-i2 p p10-50 40436.0 50436.0 40436.0 50436.0 gneg",
   "10-i3 p p10-50 40436.0 50436.0 40436.0 50436.0 gneg",
   "10-i6 p p10-50 40436.0 50436.0 40436.0 50436.0 gneg",
   "10-i7 p p10-50 40436.0 50436.0 40436.0 50436.0 gneg"]}
```
