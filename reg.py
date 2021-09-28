# reg.py
from sys import exit, argv
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QLabel,
    QMainWindow,
    QGridLayout,
    QDesktopWidget,
)
from PyQt5.QtCore import Qt

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


def setLayout():
    label = QLabel("Hello, World!")
    label.setAlignment(Qt.AlignCenter)

    layout = QGridLayout()
    layout.addWidget(label, 0, 0)

    return layout


def main():
    app = QApplication(argv)

    layout = setLayout()
    frame = QFrame()
    frame.setLayout(layout)

    window = QMainWindow()
    window.setWindowTitle("Princeton University Class Search")
    window.setCentralWidget(frame)
    screen_size = QDesktopWidget().screenGeometry()
    window.resize(screen_size.width() // 2, screen_size.height())

    window.show()
    exit(app.exec_())


if __name__ == "__main__":
    main()
