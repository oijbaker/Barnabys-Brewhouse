""" python script to provide sales predictions for Barnaby's Brewhouse by
analysis of previous sales data, and facilitate inventory management and beer
production planning """
# import libraries
from tkinter import filedialog
from tkinter import*
import matplotlib.pyplot as plt
from datetime import datetime, date
import tkinter.messagebox
from functools import partial
import logging


def get_data() -> dict:
    """ retrieve the sales data from the CSV file """
    # open the file and read the data
    with open("files/sales.csv", "r") as data_file:
        read_file = data_file.readlines()
        data = {}
        # split the data from each line by commas, and append it to the data
        # list
        fields = read_file[0].rstrip("\n").split(",")
        for n in range(6):
            data[fields[n]] = []

        for line in read_file:
            if line != read_file[0]:
                try:
                    data_in_line = line.rstrip("\n").split(",")
                    data_in_line[4] = str(int(data_in_line[4]))
                    for n in range(6):
                        data[fields[n]].append(data_in_line[n])
                except:
                    continue
    return data


def plot_data() -> None:
    """ create a graph of the sales data """
    month_data = get_month_data()
    data = []
    xlabel = []
    # create the data array for the x axis
    for key in month_data:
        data.append(month_data[key])
        xlabel.append(key)

    # plot the graph and label the axis
    plt.bar(xlabel, data, color="#b3ecff")
    plt.ylabel('Sales')
    plt.xlabel('Month')
    plt.show()


def get_month_data() -> dict:
    """ find sales data per month """
    # get the relevant data from the file
    data = get_data()
    sales_data = data["Quantity ordered"]
    date_data = data["Date Required"]

    # add up the quantities sold for each month
    month_data = {}
    for q_index in range(len(sales_data)):
        sales_no = sales_data[q_index]
        date = date_data[q_index]
        month = date[3:6]
        try:
            month_data[month] += int(sales_no)
        except:
            month_data[month] = int(sales_no)

    return month_data


def capitalise_first(string: str) -> str:
    """ capitalise the first letter of a string """
    # split the string, capitalise the first letter and rejoin it
    string = list(string)
    string[0] = string[0].upper()
    string = ''.join(string)
    return string


def predict_new() -> int:
    """ predict a new value for the sales demand next month """
    month_data = get_month_data()

    # create a dictionary of each month and the ratio to the next month
    ratios_dict = {}
    for month in MONTHS:
        month_index = MONTHS.index(month)

        month = capitalise_first(month)

        next_month = MONTHS[(month_index+1) % 12]
        next_month = capitalise_first(next_month)

        ratio = month_data[next_month]/month_data[month]
        ratios_dict[month] = ratio

    # get the names of the current month and the next month
    calculate_date = datetime.now()
    calculate_date = str(calculate_date)[5:7]

    previous_date = MONTHS[(int(calculate_date)-2) % 12]
    current_date = MONTHS[(int(calculate_date)-1) % 12]
    calculate_date = MONTHS[int(calculate_date) % 12]

    previous_date = capitalise_first(previous_date)
    current_date = capitalise_first(current_date)
    calculate_date = capitalise_first(calculate_date)

    # get the ratio for both months, and predict the next demand
    calculate_ratio = ratios_dict[calculate_date]
    current_ratio = ratios_dict[current_date]

    # the prediction is last month's data multiplied by the ratio for
    # each month
    input_sales = month_data[previous_date]
    this_prediction = int(input_sales)*current_ratio
    next_prediction = this_prediction*calculate_ratio

    # display these results on the GUI
    this_text.set(str(int(int(this_prediction)/2))+" litres")
    next_text.set(str(int(int(next_prediction)/2))+" litres")


def get_data_list() -> list:
    """ return the same information as get_data, but in a list form """
    # get the data dictionary
    data_dict = get_data()
    # put each item of the dictionary into a list
    data_list_row = []
    for key in data_dict:
        data_list_row.append(data_dict[key])
    data_list = []

    # create blank lists for each list to go into the data list
    for l in range(len(data_list_row[0])):
        data_list.append([])

    # put each item from the rows in data_list_row into the list. We now have
    # the data in the format [[invoice no. 1, customer 1, date 1, etc...],...]
    for i in range(len(data_list_row)):
        for n in range(len(data_list_row[i])):
            data_list[n].append(data_list_row[i][n])

    # check whether the data is in the correct format
    for value in data_list:
        try:
            value[2] = datetime.strptime(value[2], "%d-%b-%y")
        except:
            debug = "Date for {} stored in the wrong format".format(value[0])
            logger.debug(debug)

    # sort the list into chronological order
    sorted(data_list, key=lambda x: data_list[2])
    return data_list


def get_beer_ratios(type: int) -> list:
    """ returns the ratios of the beers, and the total number of each beer """

    # type is a variable used to represent whether the calculation is to be
    # done for this month (0), or the next month (1)

    # work out the current month as a nyumber, e.g. January = 1
    if type == 0:
        comparison_text = this_text.get().rstrip(" litres")
        comparison = int(comparison_text)
        offset = 0
        current_date = date.today().strftime("%B")
    # work out the next month as a number
    else:
        comparison_text = next_text.get().rstrip(" litres")
        comparison = int(comparison_text)
        offset = 1
        current_date = (date.today().month+1) % 12
        current_date = datetime(year=1, month=current_date, day=1)
        current_date = current_date.strftime("%B")

    # get the data as a list
    data = get_data_list()
    beers = {}

    # for each sale, if the date matches the date that we are counting for,
    # add one to a counter which is stored with that month
    for entry in data:
        try:
            match_date = MONTHS[(entry[2].month)-1]
        except:
            day = int(entry[2][0:2])
            month = entry[2][3:6]
            year = int(entry[2][7:])
            month = MONTHS.index(month.lower())
            entry[2] = datetime(year=year, month=month, day=day)
            match_date = MONTHS[(entry[2].month)-1]

        if current_date.lower()[0:3] == match_date:
            beer_name = entry[3]
            try:
                beers[beer_name] += 1
            except:
                beers[beer_name] = 1

    # add all the beers to the beer_list, and all the corresponding totals to
    # total_list
    beer_list = []
    total_list = []
    for beer in beers:
        beer_list.append(beer)
        total_list.append(beers[beer])

    # find the total number of sales
    total = 0
    for value in total_list:
        total += value

    # calculate each ratio from month to month
    beer_ratios = []
    for value in total_list:
        ratio = comparison * (value/total)
        beer_ratios.append(int(ratio))

    return beer_ratios, beer_list


def get_info(type: int) -> None:
    """ creates a window which displays the number of each beers to be made """
    # get the beers and ratios
    beer_ratios, beer_list = get_beer_ratios(type)

    # create the window
    info_window = Toplevel(bg="#515151")
    info_window.geometry("210x75")

    # create labels for each beer
    n = 0
    for beer in beer_list:
        beer_1 = Label(info_window,
                       text=beer+": "+str(beer_ratios[n])+" litres")
        beer_1.grid(row=n, column=0)
        beer_1.config(bg="#515151", fg="white", font=("Arial Black", "10"))
        n += 1


def verify_date(date: str) -> datetime:
    """ checks whether a date is in the correct format. If it is, return the
    date, otherwise, return False"""
    try:
        # check to see if the date can be parsed correctly
        date_str = date
        date_datetime = datetime.strptime(date_str, "%d-%b-%Y")
        return date
    except:
        return False


def submit_sale(window_widgets: list, sale_window: tkinter.Toplevel) -> None:
    """ the user will enter a sale and this functio will validate it, and update
    the system with the effects of the sale """

    # get all the values from the input boxes
    invoice = window_widgets[0].get()
    customer = window_widgets[1].get()
    date = window_widgets[2].get()
    beer = window_widgets[3]
    gyle = window_widgets[4].get()
    quantity = window_widgets[5].get()
    logger.info("Sale submitted")

    # put the values in a list
    info_list = [invoice, customer, date, beer, gyle, quantity]

    # check whether all the number fields are numbers
    try:
        invoice = str(int(invoice))
        gyle = str(int(gyle))
        quantity = str(int(quantity))
    except:
        # return an error message
        logger.info("Sale submit incorrectly - invalid string")
        tkinter.messagebox.showinfo("Error", "Please input a valid entry")
        return None

    # check the format of the date
    date_verification = verify_date(date)
    if date_verification is False:
        # return an error message
        logger.info("Sale submit incorrectly - Date format incorrect")
        tkinter.messagebox.showinfo("Error",
                                    ("Please enter date in the format \n",
                                     "DD-Month-YYYY"))
        return None

    # check whether all the boxes are filled in
    for item in info_list:
        if item == "":
            logger.info("Sale submit incorrectly - Missing value")
            tkinter.messagebox.showinfo("Error",
                                        "Please enter a value in all fields")
            return None

    beer = beer.get()
    # add to CSV file
    try:
        # update the stocks
        stock_updated = update_stock(beer, -int(quantity))
        if stock_updated:
            sale_window.destroy()
            logger.info("Sale logged successfully")
        else:
            raise ValueError

        csv_file = open("files/sales.csv", "a")
        write_string = ""
        for n in range(len(info_list)-1):
            write_string += str(info_list[n])+","
        write_string += info_list[len(info_list)-1]
        write_string += "\n"
        csv_file.write(write_string)
        csv_file.close()
    except:
        logger.error("Failed to log sale - file is being edited")
        tkinter.messagebox.showinfo("Error", "Please close the sales file")


def add_sale() -> None:
    """ creates a window where the user can register a sale """
    # create the fields and submit button
    sale_window = Toplevel(bg="#515151")
    sale_window.geometry("800x100")

    invoice = Label(sale_window, text="Invoice No.")
    invoice.grid(row=1, column=0)
    invoice.config(bg="#515151", fg="white", font=("Arial Black", "10"))
    invoice_field = Entry(sale_window)
    invoice_field.grid(row=2, column=0, sticky="NSEW")

    customer = Label(sale_window, text="Customer")
    customer.grid(row=1, column=1, sticky="NSEW")
    customer.config(bg="#515151", fg="white", font=("Arial Black", "10"))
    customer_field = Entry(sale_window)
    customer_field.grid(row=2, column=1, sticky="NSEW")

    date = Label(sale_window, text="Date - DD-Month-YYYY")
    date.grid(row=1, column=2, sticky="NSEW")
    date.config(bg="#515151", fg="white", font=("Arial Black", "10"))
    date_field = Entry(sale_window)
    date_field.grid(row=2, column=2, sticky="NSEW")

    beer = Label(sale_window, text="Recipe")
    beer.grid(row=1, column=3, sticky="NSEW")
    beer.config(bg="#515151", fg="white", font=("Arial Black", "10"))
    beer_select = StringVar()
    beer_field = OptionMenu(sale_window, beer_select, "Organic Red Helles",
                            "Organic Pilsner", "Organic Dunkel")
    beer_field.grid(row=2, column=3, sticky="NSEW")

    gyle = Label(sale_window, text="Gyle No.")
    gyle.grid(row=1, column=4, sticky="NSEW")
    gyle.config(bg="#515151", fg="white", font=("Arial Black", "10"))
    gyle_field = Entry(sale_window)
    gyle_field.grid(row=2, column=4, sticky="NSEW")

    quantity = Label(sale_window, text="Quantity")
    quantity.grid(row=1, column=5, sticky="NSEW")
    quantity.config(bg="#515151", fg="white", font=("Arial Black", "10"))
    quantity_field = Entry(sale_window)
    quantity_field.grid(row=2, column=5, sticky="NSEW")

    window_widgets = [invoice_field, customer_field, date_field, beer_select,
                      gyle_field, quantity_field]
    submit = Button(sale_window, text="Submit",
                    command=lambda: submit_sale(window_widgets, sale_window))
    submit.grid(row=3, column=0, sticky="NSEW")
    submit.config(fg="#515151", bg="#b3ecff", font=("Arial Black", "10"))


def start_machine(arguments: list) -> None:
    """ changes the status of the machine to be running """
    machine = arguments[0]
    machine_label = arguments[1]

    # check if the machine is empty, in which case it cannot run.
    if machines[machine][1] != "":
        machines[machine][5] = "Running"
        machine_label.config(fg="green")

    else:
        tkinter.messagebox.showinfo("Error", "Machine is empty")


def create_widgets(view_window: tkinter.Toplevel) -> None:
    """ refresh the widgets in the view window """

    # clear the existing widgets
    widget_list = view_window.winfo_children()

    for item in widget_list:
        if item.winfo_children():
            widget_list.extend(item.winfo_children())

    for item in widget_list:
        item.grid_forget()

    # make the machine labels and start buttons
    n = 2
    machine_labels = []
    for machine in machines:
        message = machine+": "+machines[machine][0]+": "+machines[machine][1]
        machine_label = Label(view_window, text=message)
        machine_label.grid(row=n, column=0)
        machine_label.config(bg="#515151", fg="white",
                             font=("Arial Black", "10"))
        machine_button = Button(view_window, text="Start")
        machine_button.grid(row=n, column=1)
        machine_button.config(command=partial(start_machine,
                                              [machine, machine_label]),
                              fg="#515151", bg="#b3ecff",
                              font=("Arial Black", "10"))
        machine_labels.append(machine_label)
        n += 1

    # make the batch labels and buttons
    batch_title = Label(view_window, text="Batch Status:")
    batch_title.grid(row=n, column=0, sticky="W")
    batch_title.config(bg="#515151", fg="white", font=("Arial Black", "10"))
    n += 1
    for batch in status:
        if status[batch] != []:
            message = batch+": "+status[batch][0]
            batch_label = Label(view_window, text=message)
            batch_label.grid(row=n, column=0)
            batch_label.config(bg="#515151", fg="white",
                               font=("Arial Black", "10"))
            batch_button = Button(view_window, text="Next Stage")
            batch_button.config(command=partial(next_stage,
                                                [batch, batch_label,
                                                 batch_button, view_window,
                                                 machine_labels]),
                                fg="#515151", bg="#b3ecff",
                                font=("Arial Black", "10"))
            batch_button.grid(row=n, column=1, sticky="NSEW")
        n += 1

    add_button = Button(view_window, text="Edit Brewing Process",
                        command=lambda: add_process(machine_labels,
                                                    view_window))
    add_button.grid(row=0, column=0, sticky="NSEW")
    add_button.config(fg="#515151", bg="#b3ecff", font=("Arial Black", "10"))
    brewers_title = Label(view_window, text="Brewing Tank Status:")
    brewers_title.config(bg="#515151", fg="white", font=("Arial Black", "10"))
    brewers_title.grid(row=1, column=0, sticky="W")


def submit_entry(view_window: tkinter.Toplevel, beer: str, gyle: str,
                 quantity: str) -> None:
    """ validate the entry of the beer into a machine and change the status
    of the batch to be the first stage of the brewing process """

    # raise an error if there is an empty box
    if beer == "" or gyle == "" or quantity == "":
        tkinter.messagebox.showinfo("Error, please fill out all fields")
    # raise an error if the gyle number is not unique
    elif gyle in status:
        tkinter.messagebox.showinfo("Error, gyle number must be unique")
    else:
        # is the gyle number a number
        try:
            gyle = str(int(gyle))
            # if no error, then set the batch to hot brew, and refresh
            # the window
            create_widgets(view_window)
            save()
        except:
            # raise an error
            logger.info("Batch load unsuccesful - Gyle is a number")
            tkinter.messagebox.showinfo("Error, gyle number must be a number")
        # repeat for the quantity
        try:
            quantity = str(int(quantity))
            status[gyle] = ["Hot Brew", beer, quantity]
            logger.info("Batch {} loaded successfully".format(gyle))
            create_widgets(view_window)
            save()
        except:
            logger.info("Batch load unsuccesful - Quantity is a number")
            tkinter.messagebox.showinfo("Error, quantity must be a number")


def machine_clear(batch: str, view_window: tkinter.Toplevel,
                  machine_labels: list) -> None:
    """ clear the machine and set its status to running """
    # clear the machine and set its status to running
    for machine in machines:
        if batch in machines[machine][1]:
            machine_list = [machine for machine in machines]
            machines[machine][1] = ""
            machines[machine][2] = ""
            machines[machine][4] = 0
            machines[machine][5] = "Waiting"
            index = machine_list.index(machine)
            machine_labels[index].config(fg="white")
            logger.info("Machine {} was cleared of {}".format(machine, batch))
    # save the files and refresh the window
    save()
    create_widgets(view_window)


def find_machine(batch: str, view_window: tkinter.Toplevel, type: str) -> str:
    """ find an appropraite machine for the batch """
    # find the volumne of the batch
    batch_info = status[batch]
    volume = float(batch_info[2])*0.5

    # find machines that aren't waiting, and can perform the correct job
    possible_machines = []
    for machine in machines:
        if type in machines[machine][0]:
            if machines[machine][5] == "Waiting":
                possible_machines.append(machine)

    machines_list = [machine for machine in possible_machines]
    n = 0
    # for every machine in possible machines, check whether it can take the job
    while n < len(machines_list):
        info = machines[machines_list[n]]
        # if there is no space in the machine, move on
        if float(info[4])+volume > float(info[3]):
            n += 1
            continue
        keys = [machine for machine in machines]
        machine_index = keys.index(machine)
        # if the machine is empty, add it
        if info[2] == "":
            return machines_list[n]
        # if the machine has the same recipe in it, add it
        elif batch_info[0] in info[2]:
            return machines_list[n]
        n += 1
    logger.info("All machines full or in use")
    tkinter.messagebox.showinfo("Error", "No Machines Available")
    return "None"


def machine_load(batch: str, view_window: tkinter.Toplevel, type: str) -> None:
    """ load a batch into a machine """
    # get an available
    machine = find_machine(batch, view_window, type)
    if machine != "None":
        # change the attributes of the machine
        new_info = [batch, status[batch][1], status[batch][2]]
        machines[machine][1] += " "+batch
        machines[machine][2] += status[batch][1]
        status_2 = int(status[batch][2])
        machines_4 = float(machines[machine][4])
        machines[machine][4] = machines_4+status_2
        # save the changes and update the window
        logger.info("{} loaded into {}".format(batch, machine))
        save()
        create_widgets(view_window)


def next_stage(arguments: list) -> None:
    """ move the batch onto the next stage of the brewing process """
    # unpack the arguments
    batch = arguments[0]
    label = arguments[1]
    button = arguments[2]
    view_window = arguments[3]
    machine_labels = arguments[4]

    # find the current stage of the batch
    current_stage = status[batch][0]
    if current_stage == "Bottling":
        # remove the batch from the window
        update_stock(status[batch][1], status[batch][2])
        status.pop(batch)
        button.grid_forget()
        label.grid_forget()
        save()
        return None

    # find the stage
    stage_index = PROCESS.index(current_stage)
    next_process = PROCESS[stage_index+1]

    if next_process == "Bottling":
        for machine in machines:
            current_machine = machines[machine]
            if current_machine[5] == "Waiting" and batch in current_machine[1]:
                tkinter.messagebox.showinfo("Error. Machine is not running")
                logger.info("{} finished brewing".format(batch))
                return None
        # remove it from the machine
        machine_clear(batch, view_window, machine_labels)
        status[batch][0] = next_process
        new_text = batch+": "+next_process
        label.config(text=new_text)
        logger.info("{} is now at stage {}".format(batch, next_process))
    elif next_process == "Fermentation":
        # load the batch
        machine_load(batch, view_window, "Fermenter")
        # update the batch's status
        status[batch][0] = next_process
        new_text = batch+": "+next_process
        label.config(text=new_text)
        logger.info("{} is now at stage {}".format(batch, next_process))
    elif next_process == "Conditioning":
        # check if the machine is running
        machine_list = [machine for machine in machines]
        for machine in machines:
            current_machine = machines[machine]
            if current_machine[5] == "Waiting" and batch in current_machine[1]:
                tkinter.messagebox.showinfo("Error. Machine is not running")
                return None
        # load it into a fermenter
        machine_clear(batch, view_window, machine_labels)
        machine_load(batch, view_window, "Conditioner")

        # update the batch's status
        status[batch][0] = next_process
        new_text = batch+": "+next_process
        label.config(text=new_text)
        logger.info("{} is now at stage {}".format(batch, next_process))

    create_widgets(view_window)
    save()
    refresh()


def add_process(machine_labels: list, view_window: tkinter.Toplevel) -> None:
    """ creates a window to allow the user to add a process """
    # make the window
    add_window = Toplevel(bg="#515151")

    # make the fields
    beer = Label(add_window, text="Recipe")
    beer.grid(row=1, column=0, sticky="NSEW")
    beer.config(bg="#515151", fg="white", font=("Arial Black", "10"))
    beer_select = StringVar()
    beer_field = OptionMenu(add_window, beer_select, "Organic Red Helles",
                            "Organic Pilsner", "Organic Dunkel")
    beer_field.grid(row=2, column=0, sticky="NSEW")

    gyle = Label(add_window, text="Gyle No.")
    gyle.grid(row=1, column=1, sticky="NSEW")
    gyle.config(bg="#515151", fg="white", font=("Arial Black", "10"))
    gyle_field = Entry(add_window)
    gyle_field.grid(row=2, column=1, sticky="NSEW")

    quantity = Label(add_window, text="Quantity")
    quantity.grid(row=1, column=2, sticky="NSEW")
    quantity.config(bg="#515151", fg="white", font=("Arial Black", "10"))
    quantity_field = Entry(add_window)
    quantity_field.grid(row=2, column=2, sticky="NSEW")

    info_widget_list = [beer_field, gyle_field, quantity_field]

    submit = Button(add_window, text="Submit",
                    command=lambda: submit_entry(view_window,
                                                 beer_select.get(),
                                                 gyle_field.get(),
                                                 quantity_field.get()))
    submit.config(fg="#515151", bg="#b3ecff", font=("Arial Black", "10"))
    submit.grid(row=3, column=0, sticky="NSEW")


def view_process() -> None:
    """ creates a window to view the machines and batches in """
    view_window = Toplevel(bg="#515151")
    create_widgets(view_window)


def save() -> None:
    ''' save the contents of the machines and batches so that they can be
    restored later '''
    # clear both files
    machines_write = open("files/machines.txt", "w")
    machines_write.close()
    batches_write = open("files/batches.txt", "w")
    batches_write.close()

    # update the files
    machines_file = open("files/machines.txt", "a")
    for machine in machines:
        machine_string = machine
        for m in machines[machine]:
            machine_string += ","+str(m)
        machines_file.write(machine_string+"\n")
    machines_file.close()

    batches_file = open("files/batches.txt", "a")
    for batch in status:
        batch_string = batch
        for b in status[batch]:
            batch_string += ","+str(b)
        batches_file.write(batch_string+"\n")
    batches_file.close()
    logger.info("Saved")


def update_stock(recipe: str, value: str) -> bool:
    """ change the value stored in the stock array """
    # find the index of the beer
    stock_index = RECIPES.index(recipe)
    # update the value
    new_stock = stocks[stock_index] - int(value)
    if new_stock < 0:
        logger.error("Stock cannot be negative")
        return False
    stocks[stock_index] += int(value)
    get_stocks()
    save_stock()
    logger.info("Stock updated {} {} {}".format("Red Helles: "+str(stocks[0]),
                                                "Pilsner: "+str(stocks[1]),
                                                "Dunkel: "+str(stocks[2])))
    return True


def recommend_beer() -> None:
    """ recommends the beer to be brewed next """
    # get information
    beer = ""
    ratio_1, beer_1 = get_beer_ratios(0)
    ratio_2, beer_2 = get_beer_ratios(1)

    considered = [False, False, False]
    for n in range(3):
        # if the stock level is below 100, recommend that it is brewed
        if stocks[n] < 100:
            beer = RECIPES[n]
            recommended.config(text=beer)
        # if the stock is less than required, consider it to be recommended
        if stocks[n] <= ratio_1[n]+ratio_2[n]:
            considered[n] = ratio_1[n]+ratio_2[n]-stocks[n]

    # if the beer hasn't been selected yet
    if beer == "":
        considered_length = [num for num in considered if num is not False]
        # if no beer is understocked, recommend the beer with the lowest stock
        if len(considered_length) == 0:
            beer_index = stocks.index(min(stocks))
        else:
            # find the biggest difference between the required amount and the
            # current stock, and recommned that beer
            maximum = max(considered)
            beer_index = considered.index(maximum)
        beer = RECIPES[beer_index]
        recommended.config(text=beer)

    logger.info("{} recommended to brew".format(beer))
    window.update()


def get_stocks() -> None:
    """ set the text and colour of the stock attributes """
    helles_text.set(str(stocks[0]))
    pilsner_text.set(str(stocks[1]))
    dunkel_text.set(str(stocks[2]))

    if stocks[0] < 100:
        helles_stock.config(fg="red")
    else:
        helles_stock.config(fg="white")
    if stocks[1] < 100:
        pilsner_stock.config(fg="red")
    else:
        pilsner_stock.config(fg="white")
    if stocks[2] < 100:
        dunkel_stock.config(fg="red")
    else:
        dunkel_stock.config(fg="white")


def refresh() -> None:
    """ run the functions to refresh the main page """
    get_stocks()
    predict_new()
    recommend_beer()


def save_stock() -> None:
    """ rewrite the stocks file """
    stock_file = open("files/stocks.txt", "w")
    stock_file.write(str(stocks[0])+","+str(stocks[1])+","+str(stocks[2])+"\n")
    stock_file.close()
    logger.info("Stock saved")


PROCESS = ["Hot Brew", "Fermentation", "Conditioning", "Bottling"]

# unpack from the stocks file
status = {}
status_file = open("files/batches.txt", "r")
status_read = status_file.readlines()
for line in status_read:
    line_split = line.rstrip("\n").split(",")
    status_key = line_split[0]
    if status_key != "":
        line_split.remove(line_split[0])
        status[status_key] = [line_split[0], line_split[1], line_split[2]]
status_file.close()

# machines dictionary stores name, type, batches in the machine, capacity and
# current volume
machines = {}
machine_file = open("files/machines.txt", "r")
machine_read = machine_file.readlines()
for line in machine_read:
    line_split = line.rstrip("\n").split(",")
    machine_key = line_split[0]
    line_split.remove(line_split[0])
    machines[machine_key] = line_split
machine_file.close()

stock_file = open("files/stocks.txt", "r")
stock_read = stock_file.readlines()
stocks = stock_read[0].rstrip("\n").split(",")
stocks = [int(stock) for stock in stocks]
stock_file.close()

MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep",
          "oct", "nov", "dec"]
FULL_MONTHS = ["January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December"]
info_widgets = {}

RECIPES = ["Organic Red Helles", "Organic Pilsner", "Organic Dunkel"]

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('files/logfile.log')
logging_format = '%(asctime)s : %(levelname)s : %(name)s : %(message)s'
formatter = logging.Formatter(logging_format)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# GUI setup
window = Tk()
window.geometry("575x325")
window.config(bg="#515151")
window.title("Barnaby's Brewhouse")

title = Label(window, text="BARNABY'S BREWHOUSE")
title.grid(row=0, column=0, sticky="NSEW", columnspan=3)
title.config(bg="#515151", fg="white", font=("Arial", 28))

calculate_date = datetime.now()
calculate_date = str(calculate_date)[5:7]

current_date = FULL_MONTHS[(int(calculate_date)-1) % 12]
calculate_date = FULL_MONTHS[int(calculate_date) % 12]

this_month = Label(window, text="Demand for "+current_date+":")
this_month.grid(row=2, column=0, sticky="NSEW")
this_month.config(bg="#515151", fg="white", font=("Arial Black", "10"))

this_info = Button(window, text="More Info", command=lambda: get_info(0))
this_info.grid(row=4, column=0, sticky="NSEW")
this_info.config(fg="#515151", bg="#b3ecff", font=("Arial Black", "10"))

next_info = Button(window, text="More Info", command=lambda: get_info(1))
next_info.grid(row=4, column=1, sticky="NSEW")
next_info.config(fg="#515151", bg="#b3ecff", font=("Arial Black", "10"))

next_month = Label(window, text="Demand for "+calculate_date+":")
next_month.grid(row=2, column=1, sticky="NSEW")
next_month.config(bg="#515151", fg="white", font=("Arial Black", "10"))

this_text = StringVar()
this_value = Label(window, textvariable=this_text)
this_value.grid(row=3, column=0, sticky="NSEW")
this_value.config(bg="#515151", fg="white", font=("Arial Black", "10"))

next_text = StringVar()
next_value = Label(window, textvariable=next_text)
next_value.grid(row=3, column=1, sticky="NSEW")
next_value.config(bg="#515151", fg="white", font=("Arial Black", "10"))

graph_button = Button(window, text="Plot Monthly Data", command=plot_data)
graph_button.grid(row=5, column=0, sticky="NSEW")
graph_button.config(fg="#515151", bg="#b3ecff", font=("Arial Black", "10"))

manage_button = Button(window, text="Add Data", command=add_sale)
manage_button.grid(row=6, column=0, sticky="NSEW")
manage_button.config(fg="#515151", bg="#b3ecff", font=("Arial Black", "10"))

view_button = Button(window, text="View Brewing Process", command=view_process)
view_button.grid(row=7, column=0, sticky="NSEW")
view_button.config(fg="#515151", bg="#b3ecff", font=("Arial Black", "10"))

pilsner_label = Label(window, text="Organic Pilsner Stock:")
pilsner_label.grid(row=8, column=0, sticky="NSEW")
pilsner_label.config(bg="#515151", fg="white", font=("Arial Black", "10"))
pilsner_text = StringVar()
pilsner_stock = Label(window, textvariable=pilsner_text)
pilsner_stock.grid(row=9, column=0, sticky="NSEW")
pilsner_stock.config(bg="#515151", fg="white", font=("Arial Black", "10"))

helles_label = Label(window, text="Organic Red Helles Stock:")
helles_label.grid(row=8, column=1, sticky="NSEW")
helles_label.config(bg="#515151", fg="white", font=("Arial Black", "10"))
helles_text = StringVar()
helles_stock = Label(window, textvariable=helles_text)
helles_stock.grid(row=9, column=1, sticky="NSEW")
helles_stock.config(bg="#515151", fg="white", font=("Arial Black", "10"))

dunkel_label = Label(window, text="Organic Dunkel Stock:")
dunkel_label.grid(row=8, column=2, sticky="NSEW")
dunkel_label.config(bg="#515151", fg="white", font=("Arial Black", "10"))
dunkel_text = StringVar()
dunkel_stock = Label(window, textvariable=dunkel_text)
dunkel_stock.grid(row=9, column=2, sticky="NSEW")
dunkel_stock.config(bg="#515151", fg="white", font=("Arial Black", "10"))

get_stocks()

recommend_label = Label(window, text="Recommended beer to brew:")
recommend_label.grid(row=10, column=0, sticky="NSEW")
recommend_label.config(bg="#515151", fg="white", font=("Arial Black", "10"))
recommended = Label(window, text="")
recommended.grid(row=10, column=1, sticky="NSEW")
recommended.config(bg="#515151", fg="white", font=("Arial Black", "10"))

refresh_button = Button(window, text="Refresh", command=refresh)
refresh_button.grid(row=11, column=0, sticky="NSEW")
refresh_button.config(fg="#515151", bg="#b3ecff", font=("Arial Black", "10"))

predict_new()
recommend_beer()

logger.info("System started successfully")
window.mainloop()
