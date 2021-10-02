# reg.py
from argparse import ArgumentParser
from sqlite3.dbapi2 import DatabaseError, OperationalError
from sys import exit, argv, stderr
from socket import socket
from pickle import load, dump
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QLabel,
    QMainWindow,
    QGridLayout,
    QDesktopWidget,
    QPushButton,
    QLineEdit,
    QListWidget,
    QMessageBox,
)
from PyQt5.QtGui import QFont

# Constants for formatting class details
ID_INDEX = 1
DAYS_INDEX = 2
START_INDEX = 3
END_INDEX = 4
BLD_INDEX = 5
ROOM_INDEX = 6
DEPT_INDEX = 7
AREA_INDEX = 8
TITLE_INDEX = 9
DESCRIPT_INDEX = 10
PREREQ_INDEX = 11
PROF_INDEX = 12

# parse the given array for the host and port
def parse_args(args):
    parser = ArgumentParser(
        description="Client for the registrar application",
        allow_abbrev=False,
    )
    parser.add_argument(
        "host",
        nargs=1,
        help="the host on which the server is running",
    )
    parser.add_argument(
        "port",
        nargs=1,
        type=int,
        help="the port at which the server is listening",
    )

    namespace = parser.parse_args(args[1:])
    return vars(namespace)


# Convert a row tuple to a string to print to the list widget
def row_to_string(row):
    str_rep = ""
    # Max widths of each column (class Id, Dept, Number, Area)
    max_widths = [5, 4, 5, 4]

    # Join the first four with the appropriate number of spaces
    for i in range(len(row) - 1):
        str_col = str(row[i])
        num_spaces = max_widths[i] - len(str_col)
        str_rep += "".join([" "] * num_spaces)
        str_rep += "".join(str_col)

    # Join the title
    str_rep += "".join(" ")
    str_rep += "".join(row[len(row) - 1])

    return str_rep


# Create a list widget from the given rows
def create_list_widget(rows):
    list_widget = QListWidget()

    list_widget.setFont(QFont("courier", 10))

    i = 0
    for row in rows:
        list_widget.insertItem(i, row_to_string(row))
        i = i + 1
    return list_widget


def update_list_widget(list_widget, rows):
    list_widget.clear()

    i = 0
    for row in rows:
        list_widget.insertItem(i, row_to_string(row))
        i = i + 1
    return list_widget


# Sends a dict to the server with class info
# returns a list of row tuples
def get_overviews(class_info, host, port, window):
    try:
        with socket() as sock:
            sock.connect((host, port))

            # Send the class info dict to the server
            out_flo = sock.makefile(mode="wb")
            dump(class_info, out_flo)
            out_flo.flush()

            print("sent command: get_overviews")

            # Read in a boolean stating if we were successful
            in_flo = sock.makefile(mode="rb")
            success = load(in_flo)
            in_flo.close()

            classes = None
            in_flo = sock.makefile(mode="rb")
            if success:
                # Read the list of rows from the server
                classes = load(in_flo)
                in_flo.close()
            else:
                raise load(in_flo)

        return classes

    # Server is unavailable
    except ConnectionRefusedError as ex:
        print("%s: " % argv[0], ex, file=stderr)
        message = "%s: " % argv[0] + str(ex)
        QMessageBox.information(window, "Server Unavailable", message)
        return None

    # Database cannot be opened
    except OperationalError as ex:
        print("%s: " % argv[0], ex, file=stderr)
        message = "A server error occurred."
        message += "Please contact the system administrator."
        QMessageBox.information(window, "Server Error", message)
        return None

    # Database is corrupted
    except DatabaseError as ex:
        print("%s: " % argv[0], ex, file=stderr)
        message = "A server error occurred."
        message += "Please contact the system administrator."
        QMessageBox.information(window, "Server Error", message)
        return None

    # Catch all other exceptions
    except Exception as ex:
        print("%s: " % argv[0], ex, file=stderr)
        exit(1)


# Sends the class Id to the server
# returns a list of tuples representing class details
def get_detail(class_id, host, port, window):
    try:
        with socket() as sock:
            sock.connect((host, port))

            # Send the class Id to the server
            out_flo = sock.makefile(mode="wb")
            dump(class_id, out_flo)
            out_flo.flush()

            print("sent command: get_detail")

            # Read in a boolean stating if we were successful
            in_flo = sock.makefile(mode="rb")
            success = load(in_flo)
            in_flo.close()

            in_flo = sock.makefile(mode="rb")
            if success:
                # Read the list of tuples from the server
                details = load(in_flo)
                in_flo.close()
            else:
                raise load(in_flo)

        return details

    # Server is unavailable
    except ConnectionRefusedError as ex:
        print("%s: " % argv[0], ex, file=stderr)
        message = "%s: " % argv[0] + str(ex)
        QMessageBox.information(window, "Server Unavailable", message)
        return None

    # Class with given class id does not exist
    except ValueError as ex:
        print("%s: " % argv[0], ex, file=stderr)
        message = "No class with class id " + class_id + " exists."
        QMessageBox.information(window, "Server Error", message)
        return None

    # Database cannot be opened
    except OperationalError as ex:
        print("%s: " % argv[0], ex, file=stderr)
        message = "A server error occurred."
        message += "Please contact the system administrator."
        QMessageBox.information(window, "Server Error", message)
        return None

    # Database is corrupted
    except DatabaseError as ex:
        print("%s: " % argv[0], ex, file=stderr)
        message = "A server error occurred."
        message += "Please contact the system administrator."
        QMessageBox.information(window, "Server Error", message)
        return None

    # Catch all other exceptions
    except Exception as ex:
        print("%s: " % argv[0], ex, file=stderr)
        exit(1)


# 5 rows by 3 columns
def set_layout(window, host, port):
    # Function for when the submit button is clicked (or equivalent)
    def submit_button_slot():
        class_info = {
            "dept": dept_edit.text(),
            "num": num_edit.text(),
            "area": area_edit.text(),
            "title": title_edit.text(),
        }

        list_fill_info = get_overviews(class_info, host, port, window)
        update_list_widget(list_widget, list_fill_info)
        add_list_widget(layout, list_widget)

    def fetch_all_classes():
        class_info = {
            "dept": "",
            "num": "",
            "area": "",
            "title": "",
        }

        list_fill_info = get_overviews(class_info, host, port, window)
        if list_fill_info is not None:
            list_widget = create_list_widget(list_fill_info)
            list_widget.activated.connect(list_click_slot)
            add_list_widget(layout, list_widget)
            return list_widget
        return None

    # Function for when a list item is double clicked (or equivalent)
    def list_click_slot():
        # Format a class dd to be a string
        # with no leading or trailing whitespace
        class_id = list_widget.currentItem().text()
        if class_id[0] == " ":
            class_id = str(class_id[1:5])
        else:
            class_id = str(class_id[:5])

        #   results = dummy_details

        results = get_detail(class_id, host, port, window)
        if results is not None:
            message = format_results(results)

            #   Activate the dialogue box with the appropriate detail
            QMessageBox.information(window, "Class Details", message)

    # Add a list widget to the layout
    def add_list_widget(layout, list_widget):
        layout.addWidget(list_widget, 4, 0, 1, 3)

    # Create the layout
    layout = QGridLayout()

    layout = add_labels(layout)

    # Create the four input fields & connect them to the submit function
    dept_edit = QLineEdit()
    dept_edit.returnPressed.connect(submit_button_slot)
    num_edit = QLineEdit()
    num_edit.returnPressed.connect(submit_button_slot)
    area_edit = QLineEdit()
    area_edit.returnPressed.connect(submit_button_slot)
    title_edit = QLineEdit()
    title_edit.returnPressed.connect(submit_button_slot)

    # Add the line edits to the layout
    layout.addWidget(dept_edit, 0, 1, 1, 1)
    layout.addWidget(num_edit, 1, 1, 1, 1)
    layout.addWidget(area_edit, 2, 1, 1, 1)
    layout.addWidget(title_edit, 3, 1, 1, 1)

    # Create the submit button & add it to the layout
    submit_button = QPushButton("Submit")
    submit_button.clicked.connect(submit_button_slot)
    layout.addWidget(submit_button, 0, 2, 4, 1)

    # Start by filling the list widget with all the classes
    # (i.e. a query with all empty strings)
    #  list_fill_info = dummy_rows
    list_widget = fetch_all_classes()

    return layout


# Helper method th add the labels to the layout
def add_labels(layout):
    # Create the four input labels
    dept_label = QLabel("Dept:")
    num_label = QLabel("Number:")
    area_label = QLabel("Area:")
    title_label = QLabel("Title:")

    # add the labels to the widget
    layout.addWidget(dept_label, 0, 0, 1, 1)
    layout.addWidget(num_label, 1, 0, 1, 1)
    layout.addWidget(area_label, 2, 0, 1, 1)
    layout.addWidget(title_label, 3, 0, 1, 1)

    return layout


# Format the class details in the proper way
def format_results(result):
    # result = results[0]

    message = ""

    # Add the first fields to the message
    message += "Course Id: " + str(result[ID_INDEX]) + "\n"
    message += "\n"
    message += "Days: " + result[DAYS_INDEX] + "\n"
    message += "Start time: " + result[START_INDEX] + "\n"
    message += "End time: " + result[END_INDEX] + "\n"
    message += "Building: " + result[BLD_INDEX] + "\n"
    message += "Room: " + result[ROOM_INDEX] + "\n"
    message += "\n"

    # print every crosslisted dept/number
    for i in range(len(result[DEPT_INDEX])):
        message += "Dept and Number: " + result[DEPT_INDEX][i] + "\n"
    message += "\n"

    # Print the area
    message += "Area: " + result[AREA_INDEX] + "\n"
    message += "\n"

    # print the title
    message += "Title: " + result[TITLE_INDEX] + "\n"
    message += "\n"

    # print the description
    message += "Description: " + result[DESCRIPT_INDEX] + "\n"
    message += "\n"

    # print the set of prerequisites
    message += "Prerequisites: " + result[PREREQ_INDEX] + "\n"

    # print the professors, if they exist
    message += "\n"
    if len(result[PROF_INDEX]) > 0:
        for i in range(len(result[PROF_INDEX])):
            message += "Professor: " + result[PROF_INDEX][i] + "\n"
    else:
        message += ""

    return message


def main():
    parsed_args = parse_args(argv)
    host = parsed_args["host"][0]
    port = parsed_args["port"][0]

    app = QApplication(argv)

    window = QMainWindow()

    # Set the layout
    layout = set_layout(window, host, port)
    frame = QFrame()
    frame.setLayout(layout)

    window.setWindowTitle("Princeton University Class Search")
    window.setCentralWidget(frame)
    screen_size = QDesktopWidget().screenGeometry()
    window.resize(screen_size.width() // 2, screen_size.height())

    window.show()
    exit(app.exec_())


if __name__ == "__main__":
    main()
