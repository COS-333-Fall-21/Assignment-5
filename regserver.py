# regserver.py
from argparse import ArgumentParser
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

# parse the given array for the host and port
def parse_args(argv):
    parser = ArgumentParser(
        description="Server for the registrar application",
        allow_abbrev=False,
    )
    parser.add_argument(
        "port",
        nargs=1,
        type=int,
        help="the port at which the server should listen",
    )

    namespace = parser.parse_args(argv[1:])
    return vars(namespace)


# query DB for all class rows that meet the parameters
def get_classes(query_args):
    for key in query_args.keys():
        query_args[key] = query_args[key].lower()
    try:
        with connect(DATABASE_URL, uri=True) as connection:
            cursor = connection.cursor()

            with closing(connection.cursor()) as cursor:
                # query set up- applies to all queries for this program
                stmt_str = (
                    "SELECT classes.classid, "
                    + "crosslistings.dept, "
                    + "crosslistings.coursenum, "
                    + "courses.area, "
                    + "courses.title "
                )
                stmt_str += "FROM crosslistings, courses, classes "
                stmt_str += "WHERE courses.courseid = classes.courseid "
                stmt_str += (
                    "AND courses.courseid = crosslistings.courseid "
                )

                # set query arguments based on command-line arguments
                if "dept" in query_args:
                    stmt_str += (
                        "AND instr(LOWER(crosslistings.dept), ?)"
                    )
                if "num" in query_args:
                    stmt_str += (
                        "AND instr(LOWER(crosslistings.coursenum), ?)"
                    )
                if "area" in query_args:
                    stmt_str += "AND instr(LOWER(courses.area), ?)"
                if "title" in query_args:
                    stmt_str += "AND instr(LOWER(courses.title), ?)"
                print('pre-executing query')
                # execute the query
                cursor.execute(stmt_str, list(query_args.values()))
                print('post-executing query')

                rows = cursor.fetchall()
                # because sorting is stable, we do the tertiary sort,
                # then the secondary, then the primary
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
                results = []
                print('pre query')
                #-------------------------------------------------#
                # select row in classes table with classid class_id
                stmt_str = "SELECT * "
                stmt_str += "FROM classes "
                stmt_str += "WHERE classes.classid = ? "

                # execute the query
                cursor.execute(stmt_str, [class_id])

                rows = cursor.fetchall()

                # append all elements from this query
                for row in rows:
                    for element in row:
                        results.append(element)

                # throw an error if there is no matching class
                if len(results) == 0:
                    raise ValueError

                COURSE_ID_INDEX = 1
                courseid = results[COURSE_ID_INDEX]
                print('post classes query')
                #-----------------------------------------#
                # select rows in crosslistings table where
                # courseid = classes.courseid
                stmt_str = "SELECT * "
                stmt_str += "FROM crosslistings "
                stmt_str += "WHERE crosslistings.courseid = ? "

                # execute the query
                cursor.execute(stmt_str, [courseid])

                rows = cursor.fetchall()

                QUERY_DEPT_INDEX = 1
                QUERY_COURSENUM_INDEX = 2
                RESULTS_DEPT_INDEX = 7
                RESULTS_COURSENUM_INDEX = 8
                results.append([])
                results.append([])
                for row in rows:
                    results[RESULTS_DEPT_INDEX].append(
                        row[QUERY_DEPT_INDEX])
                    results[RESULTS_COURSENUM_INDEX].append(
                        row[QUERY_COURSENUM_INDEX])

                # throw an error if there is no matching course
                if len(rows) == 0:
                    raise ValueError
                print('post crosslistings query')
                #-----------------------------------------#
                # select row from courses table where courseid = classes.courseid
                stmt_str = "SELECT * "
                stmt_str += "FROM courses "
                stmt_str += "WHERE courses.courseid = ? "

                # execute the query
                cursor.execute(stmt_str, [courseid])

                rows = cursor.fetchall()

                # throw an error if there is no matching course
                if len(rows) == 0:
                    raise ValueError

                # skip appending coursenum again, just append
                # area, title, descrip, and prereqs
                #results.append(rows[0][1:])
                print(rows)
                for i in range(len(rows[0])-1):
                    results.append(rows[0][i+1])

                print('post courses query')
                #-----------------------------------------#
                # select rows from coursesprofs table where 
                # courseid = classes.courseid
                stmt_str = "SELECT * "
                stmt_str += "FROM coursesprofs "
                stmt_str += "WHERE coursesprofs.courseid = ? "

                # execute the query
                cursor.execute(stmt_str, [courseid])

                rows = cursor.fetchall()

                # save all profids to use in the next query
                QUERY_PROFID_INDEX = 1
                profids = []
                for row in rows:
                    profids.append(
                        row[QUERY_PROFID_INDEX])

                # don't throw an error- there can vebe zero profs
                print('post coursesprofs query')
                #-----------------------------------------#
                # select rows from profs table for all selected profids
                stmt_str = "SELECT * "
                stmt_str += "FROM profs "
                stmt_str += "WHERE profs.profid = ? "
                
                results.append([])
                QUERY_PROFNAME_INDEX = 1
                RESULTS_PROFNAME_INDEX = 13
                print('len(results) =', len(results))
                print(results)
                print('len(profids) =', len(profids)) 

                for profid in profids:
                    # execute the query
                    cursor.execute(stmt_str, [profid])

                    prof_data = cursor.fetchall()
                    print('len(prof_data) =', len(prof_data))
                    print('len(prof_data[0]) =', len(prof_data[0]))
                    results[RESULTS_PROFNAME_INDEX].append(
                        prof_data[0][QUERY_PROFNAME_INDEX])

                # append the empty string if there are no profs
                if len(profids) == 0:
                    results[RESULTS_PROFNAME_INDEX].append('')
                print('after final query (profs)')

                return results
                # --------------------- old query ---------------------------#
                stmt_str = "SELECT * "
                stmt_str += "FROM classes, crosslistings, "
                stmt_str += "courses, coursesprofs, profs "
                stmt_str += "WHERE courses.courseid = classes.courseid "
                stmt_str += (
                    "AND courses.courseid = crosslistings.courseid "
                )
                stmt_str += (
                    "AND courses.courseid = coursesprofs.courseid "
                )
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
        print(
            "no class with class id %s exists" % class_id, file=stderr
        )
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
    if isinstance(client_data, dict):
        server_data = get_classes(client_data)
    elif isinstance(client_data, str):
        server_data = get_details(client_data)

    # Send the list of rows to the server
    out_flo = sock.makefile(mode="wb")
    dump(server_data, out_flo)
    out_flo.flush()
    print("Wrote to client")


def main():
    port = parse_args(argv)

    try:
        server_sock = socket()
        print("Opened server socket")
        if name != "nt":
            server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server_sock.bind(("", port))
        print("Bound server socket to port")
        server_sock.listen()
        print("Listening")
        while True:
            try:
                sock, client_addr = server_sock.accept()
                with sock:
                    print("Accepted connection for " + str(client_addr))
                    print("Opened socket for " + str(client_addr))
                    handle_client(sock)
            except Exception as ex:
                # TODO: actualy handle exceptions
                print(ex, file=stderr)
                exit(1)

    except Exception as ex:
        # TODO: actualy handle exceptions
        print(ex, file=stderr)
        exit(1)


if __name__ == "__main__":
    main()
