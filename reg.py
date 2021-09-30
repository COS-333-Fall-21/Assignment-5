# reg.py
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
DEPT_INDEX = 8
NUM_INDEX = 9
AREA_INDEX = 11
TITLE_INDEX = 12
DESCRIPT_INDEX = 13
PREREQ_INDEX = 14
PROF_INDEX = 18

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


# Sends a dict to the server with class info
# returns a list of row tuples
def get_classes(class_info):
    try:
        host = argv[1]
        port = int(argv[2])
        with socket() as sock:
            sock.connect((host, port))

            # Send the class info dict to the server
            out_flo = sock.makefile(mode="wb")
            print("Dumping...")
            print(class_info)
            print()
            dump(class_info, out_flo)
            out_flo.flush()

            # Read the list of rows from the server
            in_flo = sock.makefile(mode="rb")
            classes = load(in_flo)
            in_flo.close()

        return classes

    except Exception as ex:
        print("%s: " % argv[0], ex, file=stderr)
        exit(1)


# Sends the class Id to the server
# returns a list of tuples representing class details
def get_details(class_id):
    try:
        host = argv[1]
        port = int(argv[2])
        with socket() as sock:
            sock.connect((host, port))

            # Send the class Id to the server
            out_flo = sock.makefile(mode="wb")
            dump(class_id, out_flo)
            out_flo.flush()

            # Read the list of tuples from the server
            in_flo = sock.makefile(mode="rb")
            details = load(in_flo)
            in_flo.close()

        print(details)
        return details

    except Exception as ex:
        print("%s: " % argv[0], ex, file=stderr)
        exit(1)


list_widget = None
# 5 rows by 3 columns
def set_layout(window):
    # Function for when the submit button is clicked (or equivalent)
    def submit_button_slot():
        global list_widget
        class_info = {
            "dept": dept_edit.text(),
            "num": num_edit.text(),
            "area": area_edit.text(),
            "title": title_edit.text(),
        }

        list_fill_info = get_classes(class_info)
        list_widget = create_list_widget(list_fill_info)
        list_widget.activated.connect(list_click_slot)
        add_list_widget(layout, list_widget)

    # Function for when a list item is double clicked (or equivalent)
    def list_click_slot():
        # Format a class dd to be a string
        # with no leading or trailing whitespace
        print(list_widget.currentItem().text())
        class_id = list_widget.currentItem().text()
        if class_id[0] == " ":
            class_id = str(class_id[1:5])
        else:
            class_id = str(class_id[:5])

        #   results = dummy_details
        results = get_details(class_id)
        message = format_results(results)

        #   Activate the dialogue box with the appropriate detail
        QMessageBox.information(window, "Class Details", message)

    # Add a list widget to the layout
    def add_list_widget(layout, list_widget):
        layout.addWidget(list_widget, 4, 0, 1, 3)

    # Create the layout
    layout = QGridLayout()

    # Create the four input labels
    dept_label = QLabel("Dept:")
    num_label = QLabel("Number:")
    area_label = QLabel("Area:")
    title_label = QLabel("Title:")

    # Create the four input fields & connect them to the submit function
    dept_edit = QLineEdit()
    dept_edit.returnPressed.connect(submit_button_slot)
    num_edit = QLineEdit()
    num_edit.returnPressed.connect(submit_button_slot)
    area_edit = QLineEdit()
    area_edit.returnPressed.connect(submit_button_slot)
    title_edit = QLineEdit()
    title_edit.returnPressed.connect(submit_button_slot)

    # Start by filling the widget with all the classes
    # (i.e. a query with all empty strings)
    #  list_fill_info = dummy_rows
    submit_button_slot()

    # create the list widget
    # list_widget = create_list_widget(list_fill_info)

    # Create the submit button
    submit_button = QPushButton("Submit")
    submit_button.clicked.connect(submit_button_slot)

    layout.addWidget(dept_label, 0, 0, 1, 1)
    layout.addWidget(num_label, 1, 0, 1, 1)
    layout.addWidget(area_label, 2, 0, 1, 1)
    layout.addWidget(title_label, 3, 0, 1, 1)

    layout.addWidget(dept_edit, 0, 1, 1, 1)
    layout.addWidget(num_edit, 1, 1, 1, 1)
    layout.addWidget(area_edit, 2, 1, 1, 1)
    layout.addWidget(title_edit, 3, 1, 1, 1)

    layout.addWidget(submit_button, 0, 2, 4, 1)

    # add_list_widget(layout, list_widget)

    return layout


# Format the class details in the proper way
def format_results(results):
    result = results[0]

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
    for listing in results:
        message += (
            "Dept and Number: "
            + listing[DEPT_INDEX]
            + " "
            + listing[NUM_INDEX]
            + "\n"
        )
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
    if result[PREREQ_INDEX] != "":
        message += "Prerequisites: " + result[PREREQ_INDEX] + "\n"
    else:
        message += "Prerequisites: None" + "\n"

    # print the professors, if they exist
    if len(result) > PROF_INDEX:
        message += "\n"
        more_profs = True
        i = PROF_INDEX
        while more_profs:
            message += "Professor: " + result[i] + "\n"
            i += 1
            if len(result) <= i:
                more_profs = False

    return message


def main():
    # TODO: Actually handle this correctly using ArgParse
    if len(argv) != 3:
        print("Usage: python %s host port", argv[0])
        exit(1)

    app = QApplication(argv)

    window = QMainWindow()

    # Set the layout
    layout = setLayout(window)
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
