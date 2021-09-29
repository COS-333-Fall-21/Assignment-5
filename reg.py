# reg.py
from sys import exit, argv, stderr
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
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from socket import socket
from pickle import load, dump

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

dummy_rows = [
    (8291, "COS", "116", "ST", "The Computational Universe"),
    (8292, "COS", "126", "QR", "General Computer Science"),
    (8293, "COS", "126", "QR", "General Computer Science"),
    (8308, "COS", "217", "QR", "Introduction to C_Science Programming Systems"),
    (8313, "COS", "226", "QR", "Algorithms and Data Structures"),
    (
        9032,
        "COS",
        "233",
        "ST",
        "An Integrated, Quantitative Introduction to the Natural Sciences II",
    ),
    (
        9033,
        "COS",
        "233",
        "ST",
        "An Integrated, Quantitative Introduction to the Natural Sciences II",
    ),
    (
        9037,
        "COS",
        "234",
        "",
        "An Integrated, Quantitative Introduction to the Natural Sciences II",
    ),
    (
        9038,
        "COS",
        "236",
        "",
        "An Integrated, Quantitative Introduction to the Natural Sciences IV",
    ),
    (8597, "COS", "306", "ST", "Introduction to Logic Design"),
    (
        9363,
        "COS",
        "314",
        "QR",
        "Computer and Electronic Music through Programming, Performance, and Composition",
    ),
    (8320, "COS", "320", "", "Compiling Techniques"),
    (8321, "COS", "333", "", "Advanced C%Science Programming Techniques"),
    (9240, "COS", "342", "QR", "Introduction to Graph Theory"),
    (8322, "COS", "398", "", "Junior Independent Work (B.S.E. candidates only)"),
    (10009, "COS", "401", "", "Introduction to Machine Translation"),
    (8323, "COS", "423", "", "Theory of Algorithms"),
    (8324, "COS", "424", "", "Interacting with Data"),
    (8325, "COS", "426", "", "Computer Graphics"),
    (8326, "COS", "433", "", "Cryptography"),
    (8327, "COS", "435", "", "Information Retrieval, Discovery, and Delivery"),
    (8328, "COS", "444", "SA", "Internet Auctions: Theory and Practice"),
    (8329, "COS", "451", "", "Computational Geometry"),
    (8330, "COS", "461", "", "Computer Networks"),
    (8331, "COS", "498", "", "Senior Independent Work (B.S.E. candidates only)"),
    (8332, "COS", "522", "", "Computational Complexity"),
    (
        10244,
        "COS",
        "586",
        "",
        "Topics in STEP: Information Technology and Public Policy",
    ),
    (
        8333,
        "COS",
        "598A",
        "",
        "Advanced Topics in Computer Science: Economic and Systems Design for Electronic Marketplaces",
    ),
    (
        8334,
        "COS",
        "598B",
        "",
        "Advanced Topics in Computer Science: Algorithms and Complexity",
    ),
    (
        8335,
        "COS",
        "598C",
        "",
        "Advanced Topics in Computer Science: Systems for Large Data",
    ),
    (
        8336,
        "COS",
        "598D",
        "",
        "Advanced Topics in Computer Science: Formal Methods in Networking",
    ),
]

dummy_details = [
    (
        8292,
        3668,
        "TTh",
        "10:00 AM",
        "10:50 AM",
        "FRIEN",
        "101",
        3668,
        "COS",
        "126",
        3668,
        "QR",
        "General Computer Science",
        "An introduction to computer science in the context of scientific, engineering, and commercial applications. The goal of the course is to teach basic principles and practical issues, while at the same time preparing students to use computers effectively for applications in computer science, physics, biology, chemistry, engineering, and other disciplines. Topics include: hardware and software systems; programming in Java; algorithms and data structures; fundamental principles of computation; and scientific computing, including simulation, optimization, and data analysis. Two lectures, two precepts.",
        "",
        3668,
        313,
        313,
        "Larry L. Peterson",
    ),
    (
        8292,
        3668,
        "TTh",
        "10:00 AM",
        "10:50 AM",
        "FRIEN",
        "101",
        3668,
        "EGR",
        "126",
        3668,
        "QR",
        "General Computer Science",
        "An introduction to computer science in the context of scientific, engineering, and commercial applications. The goal of the course is to teach basic principles and practical issues, while at the same time preparing students to use computers effectively for applications in computer science, physics, biology, chemistry, engineering, and other disciplines. Topics include: hardware and software systems; programming in Java; algorithms and data structures; fundamental principles of computation; and scientific computing, including simulation, optimization, and data analysis. Two lectures, two precepts.",
        "",
        3668,
        313,
        313,
        "Larry L. Peterson",
    ),
]


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


def create_list_widget(rows):
    list_widget = QListWidget()

    list_widget.setFont(QFont("courier", 10))

    i = 0
    for row in rows:
        list_widget.insertItem(i, row_to_string(row))
        i = i + 1
    return list_widget


# Sends a dict to the server with class info; returns a list of row tuples
def get_classes(class_info):
    try:
        host = argv[1]
        port = int(argv[2])
        with socket() as sock:
            sock.connect((host, port))

            out_flo = sock.makefile(mode="wb")
            dump(class_info, out_flo)
            out_flo.flush()

            in_flo = sock.makefile(mode="rb")
            details = load(in_flo)
            in_flo.close()

        print(details)
        return details

    except Exception as ex:
        print("%s: " % argv[0], ex, file=stderr)
        exit(1)


def get_details(class_id):
    try:
        host = argv[1]
        port = int(argv[2])
        with socket() as sock:
            sock.connect((host, port))

            out_flo = sock.makefile(mode="wb")
            dump(class_id, out_flo)
            out_flo.flush()

            in_flo = sock.makefile(mode="rb")
            details = load(in_flo)
            in_flo.close()

        print(details)
        return details

    except Exception as ex:
        print("%s: " % argv[0], ex, file=stderr)
        exit(1)


# 5 rows by 3 columns
def setLayout(window):
    list_fill_info = []

    def submit_button_slot():
        class_info = {
            "dept": dept_edit.text(),
            "num": num_edit.text(),
            "area": area_edit.text(),
            "title": title_edit.text(),
        }
        list_fill_info = get_classes(class_info)

    def list_click_slot():
        class_id = format_class_id()
        # TODO: Add data to this
        results = get_details(class_id)
        message = format_results(results)
        #   print("Message:", message)
        QMessageBox.information(window, "Class Details", message)

    def format_class_id():
        class_id = list_widget.currentItem().text()
        if class_id[0] == " ":
            class_id = str(class_id[1:4])
        else:
            class_id = str(class_id[:4])
        print("Fetching info for class " + class_id + "...")
        return class_id

    dept_label = QLabel("Dept:")
    num_label = QLabel("Number:")
    area_label = QLabel("Area:")
    title_label = QLabel("Title:")

    dept_edit = QLineEdit()
    num_edit = QLineEdit()
    area_edit = QLineEdit()
    title_edit = QLineEdit()

    list_widget = create_list_widget(list_fill_info)

    submit_button = QPushButton("Submit")
    submit_button.clicked.connect(submit_button_slot)
    list_widget.clicked.connect(list_click_slot)

    layout = QGridLayout()

    layout.addWidget(dept_label, 0, 0, 1, 1)
    layout.addWidget(num_label, 1, 0, 1, 1)
    layout.addWidget(area_label, 2, 0, 1, 1)
    layout.addWidget(title_label, 3, 0, 1, 1)

    layout.addWidget(dept_edit, 0, 1, 1, 1)
    layout.addWidget(num_edit, 1, 1, 1, 1)
    layout.addWidget(area_edit, 2, 1, 1, 1)
    layout.addWidget(title_edit, 3, 1, 1, 1)

    layout.addWidget(submit_button, 0, 2, 4, 1)

    layout.addWidget(list_widget, 4, 0, 1, 3)

    return layout


def format_results(results):
    #  def wrap(wrapper, string):
    #      desc_list = wrapper.wrap(text=string)
    #      frmtd_row = desc_list[0]
    #      if len(desc_list) > 1:
    #          for i in range(len(desc_list) - 1):
    #              frmtd_row += "\n" + desc_list[i + 1]
    #      return frmtd_row

    #  wrapper = textwrap.TextWrapper(width=DEFAULT_WIDTH)

    result = results[0]

    message = ""

    message += "Course Id:" + str(result[ID_INDEX]) + "\n"
    message += "\n"
    message += "Days:" + result[DAYS_INDEX] + "\n"
    message += "Start time:" + result[START_INDEX] + "\n"
    message += "End time:" + result[END_INDEX] + "\n"
    message += "Building:" + result[BLD_INDEX] + "\n"
    message += "Room:" + result[ROOM_INDEX] + "\n"
    message += "\n"

    # print every crosslisted dept/number
    for listing in results:
        message += "Dept and Number:" + listing[DEPT_INDEX] + listing[NUM_INDEX] + "\n"
    message += "\n"

    message += "Area:" + result[AREA_INDEX] + "\n"
    message += "\n"

    # print a wrapped title
    #  frmtd_row = wrap(wrapper, "Title: " + result[TITLE_INDEX])
    #  print(frmtd_row)
    message += "Title: " + result[TITLE_INDEX] + "\n"
    message += "\n"

    # print a wrapped description
    #  frmtd_row = wrap(wrapper, "Description: " + result[DESCRIPT_INDEX])
    #  print(frmtd_row)
    message += "Description: " + result[DESCRIPT_INDEX] + "\n"
    message += "\n"

    # print a wrapped set of prerequisites
    if result[PREREQ_INDEX] != "":
        #   frmtd_row = wrap(wrapper, "Prerequisites: " + result[PREREQ_INDEX])
        #   print(frmtd_row)
        message += "Prerequisites: " + result[PREREQ_INDEX] + "\n"
    else:
        message += "Prerequisites:" + "\n"

    if len(result) > PROF_INDEX:
        message += "\n"
        more_profs = True
        i = PROF_INDEX
        while more_profs:
            message += "Professor:" + result[i] + "\n"
            i += 1
            if len(result) <= i:
                more_profs = False

    return message


def main():
    if len(argv) != 3:
        print("Usage: python %s host port", argv[0])
    app = QApplication(argv)

    window = QMainWindow()

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
