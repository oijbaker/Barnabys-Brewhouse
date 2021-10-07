# Barnaby's Brewhouse Management System
This program allows you to:
   - Keep track of sales data
   - Monitor Stock
   - Monitor brewing status

# Requirements:
Written python 3.7. Requires python 3.6+
Standard libraries:
  - tkinter
  - logging
  - datetime
  
Extra libaries
  - functools
```sh
$ pip install functools
```
  - matplotlib
 ```sh
$ pip install matplotlib
```


# Getting Started
A walkthrough of te interface:
- Demand for [month]
    - Shows the predicted brewing requirements for the month
- More info
    - Gives information on the requirements for each beer
- Plot monthly data
    - Shows a graph of sales against months
- Add data
    - Record a sale (NOTE: enter the date format as DD-Month-YYYY e.g. 05-Dec-2019)
- View brewing process
    - Show the status of each tank. Edit brewing process allows the user to add jobs
- Refresh
    - Updates the data show on the interface   
