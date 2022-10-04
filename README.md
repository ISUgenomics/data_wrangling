# data_wrangling
The **data_wrangling** repo collects Python mini-apps for popular tasks in the data processing.

Each application is placed in a separate directory for the tidy organization where you can find:
- the python script (.py) of the application
- the example inputs
- the documentation in the README.md file, including some example usage variations

All the applications have a **built-in set of options** provided as in-line arguments from the command line. Thanks to that, there is **no need to modify source code** by the user (e.g., to replace input filename or tune params). Also, it makes the apps more universal, comprehensive, and robust.

More advanced (multi-purpose or multi-options) applications have a **built-in logger** which reports the analysis progress with the details depending on the **selected verbosity level**.

## bin_data app

The application enables grouping/slicing of the data as the ensembles of rows and aggregates observables from the numerical columns by calculating the sum or mean in each group/slice.

![Bin data app](bin_data/bin_data.png)


## data_merge app

The application enables the merging of two files by matching columns and assigning custom error values for missing data.

![Merge data app](merge_data/merge_data.png)
