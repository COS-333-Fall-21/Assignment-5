#regserver.py
from sys import exit, argv, stderr
from socket import socket, SOL_SOCKET, SO_REUSEADDR
from pickle import load, dump
from os import name
import argparse
from sqlite3 import connect, OperationalError, DatabaseError
from contextlib import closing

DATABASE_URL = "file:reg.sqlite?mode=ro"

CLASS_ID_INDEX = 0
DEPT_INDEX = 1
COURSE_NUM_INDEX = 2
AREA_INDEX = 3
TITLE_INDEX = 4

# query DB for all class rows that meet the parameters
def get_classes(query_args):
    try:
        with connect(DATABASE_URL, uri=True) as connection:
            cursor = connection.cursor()

            with closing(connection.cursor()) as cursor:

                # query set up- applies to all queries for this program
                stmt_str = "SELECT classes.classid, crosslistings.dept, crosslistings.coursenum, courses.area, courses.title "
                stmt_str += "FROM crosslistings, courses, classes "
                stmt_str += "WHERE courses.courseid = classes.courseid AND courses.courseid = crosslistings.courseid "

                # set query arguments based on command-line arguments
                if "dept" in query_args:
                    stmt_str += "AND instr(LOWER(crosslistings.dept), ?)"
                if "num" in query_args:
                    stmt_str += "AND instr(LOWER(crosslistings.coursenum), ?)"
                if "area" in query_args:
                    stmt_str += "AND instr(LOWER(courses.area), ?)"
                if "title" in query_args:
                    stmt_str += "AND instr(LOWER(courses.title), ?)"

                # execute the query
                cursor.execute(stmt_str, list(query_args.values()))

                rows = cursor.fetchall()
                # because sorting is stable, we do the tertiary sort, then the secondary, then the primary
                rows.sort(key=lambda row: row[CLASS_ID_INDEX])
                rows.sort(key=lambda row: row[COURSE_NUM_INDEX])
                rows.sort(key=lambda row: row[DEPT_INDEX])

                return rows

    # Database cannot be opened
    except OperationalError as ex:
        print("%s: " % argv[0], ex, file=stderr)
        exit(1)

    # Database is corrupted
    except DatabaseError as ex:
        print("%s: " % argv[0], ex, file=stderr)
        exit(1)

    # Catch all other exceptions
    except Exception as ex:
        print("%s: " % argv[0], ex, file=stderr)
        exit(1)

# query DB for all details of one class with id class_id
def get_details(class_id):
    try:
        with connect(DATABASE_URL, uri=True) as connection:
            cursor = connection.cursor()

            with closing(connection.cursor()) as cursor:
                stmt_str = "SELECT * "
                stmt_str += "FROM classes, crosslistings, courses, coursesprofs, profs "
                stmt_str += "WHERE courses.courseid = classes.courseid "
                stmt_str += "AND courses.courseid = crosslistings.courseid "
                stmt_str += "AND courses.courseid = coursesprofs.courseid "
                stmt_str += "AND coursesprofs.profid = profs.profid "
                stmt_str += "AND classes.classid = ? "

                # execute the query
                cursor.execute(stmt_str, [class_id])

                results = cursor.fetchall()

                # throw an error if there is no matching class
                if len(results) == 0:
                    raise ValueError

                # sort based on department
                results.sort(key=lambda row: row[DEPT_INDEX])

                return results

    # Database cannot be opened
    except OperationalError as ex:
        print("%s: " % argv[0], ex, file=stderr)
        exit(1)

    # Database is corrupted
    except DatabaseError as ex:
        print("%s: " % argv[0], ex, file=stderr)
        exit(1)

    # Class with class id does not exist
    except ValueError as ex:
        print("no class with class id %s exists" % class_id, file=stderr)
        exit(2)

    # Catch all other exceptions
    except Exception as ex:
        print("%s: " % argv[0], ex, file=stderr)
        exit(1)


def handle_client(sock):
    # Read data from the client
    in_flo = sock.makefile(mode="rb")
    client_data = load(in_flo)
    in_flo.close()

    # Choose which DB query to use based on type of data from client
    if type(client_data) == dict:
        server_data = get_classes(client_data)
    elif type(client_data) == str:
        server_data = get_details(client_data)

    # Send the list of rows to the server
    out_flo = sock.makefile(mode="wb")
    dump(server_data, out_flo)
    out_flo.flush()
    print('Wrote to client')

def main():
    # TODO: Actually handle this correctly using ArgParse
    if len(argv) != 3:
        print("Usage: python %s host port", argv[0])
        exit(1)
    
    try:
        port = int(argv[1])
        server_sock = socket()
        print('Opened server socket')
        if (name != 'nt'):
            server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server_sock.bind(('', port))
        print('Bound server socket to port')
        server_sock.listen()
        print('Listening')
        while True:
            try: 
                sock, client_addr = server_sock.accept()
                with sock:
                    print('Accepted connection for ' + str(client_addr))
                    print('Opened socket for ' + str(client_addr))
                    handle_client(sock)
            except Exception as ex:
                #TODO: actualy handle exceptions
                print(ex, file=stderr)
                exit(1)

    except Exception as ex:
        #TODO: actualy handle exceptions
        print(ex, file=stderr)
        exit(1)

    

if __name__ == "__main__":
    main()
