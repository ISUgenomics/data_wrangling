# data_wrangling
Python mini-apps for common tasks in data processing

## data_merge app
The application enables merging of two files by matching columns. <br>
* both files should be a column-like text files (including Excel .xlsx format and CSV separated with different delimiters)
* both files should include a matching column (with the same values) but the header may be different in each file
* data (all columns) from second file (i.e., merge_file) is added into the first file (i.e., input_file) and automatically saved in the output file
* the user can customize the name of the output file
* the user has to provide the indexes of matching columns (numbering starts from 0) or unique headers of columns
* if some values are missing in the merge_data file, the corresponding fields are filled with pre-set missing_value (-9999.99 by default, user can customize it)

### Requirements for merge_data.py:

Requirements: python3, pandas, openpyxl, csv

### Options of merge_data.py:

```
optional arguments:
  -h,         --help                       # show this help message and exit
  -i file1,   --data-file-1 file1          # [string] input multi-col file
  -m file2,   --data-file-2 file2          # [string] merge multi-col file
  -c cols,    --matching-columns cols      # list of the same column of two files, e.g., 0,5 or label1,label2 
  -e missing, --error-value missing        # [any] provide custom value for missing data
  -o outfile, --output-datafile outfile    # [string] provide custom name for the output data_file
  -f format,  --output-format format       # [int] select format for output file: 0 - original, 1 - csv, 2 - xlsx
```

### Usage of merge_data.py:

```
data_matcher.py [-h] -i file1 -m file2 -c cols [-e missing] [-o outfile] [-f format]
```

*^ arguments provided in square brackets [] are optional*

* example usage with minimal required options: 

```
python3 merge_data.py -i input_file -m merge_file -c 1,5

python3 merge_data.py -i input_file -m merge_file -c address,Address
```

* example usage with customized value for missing data: 

```
python3 merge_data.py -i input_file -m merge_file -c 1,5 -e "missing"
```

*^ the default value for missing data is: -9999.99*

* example usage with customized name of output file:

```
python3 merge_data.py -i input_file -m merge_file -c 1,5 -o my_merged_data.txt
```

*^ the default output filename is: data_output-$date*

* example usage with Excel format of output file:

```
python3 merge_data.py -i input_file -m merge_file -c 1,5 -f 2
```

* fully customized example usage with user-provided value for missing data and output filename saved in Excel format:

```
python3 merge_data.py -i input_file -m merge_file -c 1,5 -e missing -o my_merged_data -f 2
```

