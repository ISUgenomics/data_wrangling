# bin_data.py app (python)

## Overview
The bin_data.py application is written in Python3 and employes the efficient libabries [pandas and numpy] for operating on complex data structure. The application aggregates observables [by summing or averaging numerical values] over the data slices (rows grouped in a slice). The statistic is calculated separately for each column of numerical values while 'ranges-column' (with the default 'position' header) stores starting position in the slice or range of incremented values.

The type of slices can be requested using `-t` option as:
- **steps**, where the **size of the slice** is user-provided as the number of consequtive data rows
- **bins**, where the **number of slices** is user-provided
- **value**, where the slices are cut based on the **increment of the value** in the selected (numerical) 'ranges-column' (use `-r` option to specify column index)

The slicing procedure is performed separately for each category (if multiple provided) stored in the 'labels-column', use `-l` option. If the user is interested in selected labels only, they can be provided with the `-ll` option as a one-column file or inline comma-separated string.


## Requirements

Requirements: python3, pandas, numpy

* Python3 - Ubuntu

```
sudo apt-get update
$ sudo apt-get install python3.
```

* Python3 - macOS

^ if not yet, install Homebrew
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

```
brew install python3
```

* Python3 - Windows

Please follow the instructions provided at [phoenixnap.com](https://phoenixnap.com/kb/how-to-install-python-3-windows)


* Install app requirements

```
pip3 install pandas
pip3 install numpy
```

## Options

help & info arguments:
```
  -h,         --help                    # show full help message and exit
  -v level,   --verbose level           # [int] increase verbosity: 0 = warnings, 1 = info, 2 = rich info
```

required arguments:
```
-i input,     --data-source input       # [string] input multi-col file or directory with data chunks
-l label,     --labels-col label        # [int]    index of column with labels used to chunk data
-r range,     --ranges-col range        # [int]    index of column with ranges used to slice data
```

optional arguments:
```
  -ll llist,  --label-list llist        # [path] or [comma-separated list] provide custom list of labels to be extracted; [default: None] means all to be extracted
  -hd header, --header header           # [list]            provide custom list of columns names (header); [default: None] means assigning 'label' for labels-col, 'position' for ranges-col, and 'val-X' for remaining columns, where X is an increasing int number
  -ch chunks, --chunk-size chunks       # [int]             provide custom size of chunks (number of rows loaded at once); [default: None] means optimizing number of rows for 250MB memory usage
  -s save,    --chunk-save save         # {true,false}      saves data into chunked files; [default: true] means data chunked by unique labels will be saved in CSV format into the CHUNKS/ directory
  -c calc,    --calc-stats calc         # {ave,sum}         select resizing opeartion: ave (mean) or sum; [default: 'ave'] means average of each column in the slice will be returned
  -t type,    --slice-type type         # {step,bin,value}  select type of slicing: step (number of rows in a slice) or bin (number of slices) or value (value increment in ranges-col); [default: 'step'] means data will be sliced by the number of rows in a slice (each slice consists of the same number of rows)
  -n slice,   --slice-size slice        # [float]           select size/increment of slicing; [default: 100] means the slice will be composed of 100 rows or there will be 100 slices in total or the increment for slicing will be 100
  -d dec,     --decimal-out dec         # [int]             provide decimal places for numerical outputs; [default: 2] means 2 decimal places will be kept for all numeric columns
  -o out,     --output out              # [string]          provide custom output filename; [default: 'output_data'] means that the resized output data will be saved as 'output_data.csv' file
```


## Example usage

```
bin_data.py -i input -l label -r range [-ll labels_list] [-hd header_names]
            [-ch chunks_size] [-s {true,false}]
            [-c {ave,sum}] [-t {step,bin,value}] [-n slice]
            [-d dec] [-o out]
            [-v [VERBOSE]] [-h]
```

*^ arguments provided in square brackets [] are optional*

* example usage with minimal required options:

```
python3 bin_data.py -i input_file -l 0 -r 1
```

* example usage with large raw input file:

```
python3 bin_data.py -i hybrid.depth -l 0 -r 1 -t 'step' -n 1000 -s True -v 1
```

* example usage with input directory of data chunks in CSV format:

```
python3 bin_data.py -i CHUNKS/ -l 0 -r 1 -t 'value' -n 0.15 -s False -v 0
```

* example usage with all default settings:

```
python3 bin_data.py -i {path} -l {int} -r {int} -ll None -hd None -ch None -s True -c 'ave' -t 'step' -n 100 -d 2 -o 'output_data' -v 0
```
