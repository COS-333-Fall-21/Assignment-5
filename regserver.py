# regserver.py
from argparse import ArgumentParser
from sys import exit, argv, stderr
from socket import socket, SOL_SOCKET, SO_REUSEADDR
from pickle import load, dump
from os import name
from sqlite3 import connect, OperationalError, DatabaseError
from contextlib import closing
from time import process_time
from multiprocessing import Process

DATABASE_URL = "file:reg.sqlite?mode=ro"

CLASS_ID_INDEX = 0
DEPT_INDEX = 1
COURSE_NUM_INDEX = 2
AREA_INDEX = 3
TITLE_INDEX = 4

COURSE_ID_INDEX = 1

QUERY_DEPT_INDEX = 1
QUERY_COURSENUM_INDEX = 2
RESULTS_DEPT_INDEX = 7

QUERY_PROFID_INDEX = 1

QUERY_PROFNAME_INDEX = 1
RESULTS_PROFNAME_INDEX = 12


def consume_cpu_time(delay):
    i = 0
    initial_time = process_time()
    while (process_time() - initial_time) < delay:
        i += 1


# parse the given array for the host and port
def parse_args(args):
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
    parser.add_argument(
        "delay",
        nargs=1,
        type=int,
        help="the number of seconds the server should wait when called",
    )

    namespace = parser.parse_args(args[1:])
    return vars(namespace)


# query DB for all class rows that meet the parameters
def get_overviews(query_args, sock):
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
                # execute the query
                cursor.execute(stmt_str, list(query_args.values()))

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
        send_error_to_client(ex, sock)
        return None

    # Database is corrupted
    except DatabaseError as ex:
        print("%s: " % argv[0], ex, file=stderr)
        send_error_to_client(ex, sock)
        return None

    # Catch all other exceptions
    except Exception as ex:
        print("%s: " % argv[0], ex, file=stderr)
        exit(1)


# get the class with class Id class_id and append to results
def get_class(results, cursor, class_id):
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


# get the crosslistings associated with course Id courseid
# and append to results
def get_crosslistings(results, cursor, courseid):
    # select rows in crosslistings table where
    # courseid = classes.courseid
    stmt_str = "SELECT * "
    stmt_str += "FROM crosslistings "
    stmt_str += "WHERE crosslistings.courseid = ? "

    # execute the query
    cursor.execute(stmt_str, [courseid])

    rows = cursor.fetchall()

    results.append([])
    for row in rows:
        results[RESULTS_DEPT_INDEX].append(
            row[QUERY_DEPT_INDEX] + " " + row[QUERY_COURSENUM_INDEX]
        )

    results[RESULTS_DEPT_INDEX].sort()

    # throw an error if there is no matching course
    if len(rows) == 0:
        raise ValueError


# get the course associated with course Id courseid
# and append to results
def get_course(results, cursor, courseid):
    # select row from courses table where
    # courseid = classes.courseid
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
    # results.append(rows[0][1:])
    for i in range(len(rows[0]) - 1):
        results.append(rows[0][i + 1])


# get the profs associated with the course with
# course Id course id and append to results
def get_profs(results, cursor, courseid):
    # select rows from coursesprofs table where
    # courseid = classes.courseid
    stmt_str = "SELECT * "
    stmt_str += "FROM coursesprofs "
    stmt_str += "WHERE coursesprofs.courseid = ? "

    # execute the query
    cursor.execute(stmt_str, [courseid])

    rows = cursor.fetchall()

    # save all profids to use in the next query
    profids = []
    for row in rows:
        profids.append(row[QUERY_PROFID_INDEX])

    # don't throw an error- there can be zero profs
    # -----------------------------------------#
    # select rows from profs table for all selected profids
    stmt_str = "SELECT * "
    stmt_str += "FROM profs "
    stmt_str += "WHERE profs.profid = ? "

    results.append([])

    for profid in profids:
        # execute the query
        cursor.execute(stmt_str, [profid])

        prof_data = cursor.fetchall()
        results[RESULTS_PROFNAME_INDEX].append(
            prof_data[0][QUERY_PROFNAME_INDEX]
        )

    results[RESULTS_PROFNAME_INDEX].sort()

    # append the empty string if there are no profs
    if len(profids) == 0:
        results[RESULTS_PROFNAME_INDEX].append("")


# query DB for all details of one class with id class_id
def get_detail(class_id, sock):
    try:
        with connect(DATABASE_URL, uri=True) as connection:
            cursor = connection.cursor()

            with closing(connection.cursor()) as cursor:
                results = []

                get_class(results, cursor, class_id)

                courseid = results[COURSE_ID_INDEX]
                get_crosslistings(results, cursor, courseid)

                get_course(results, cursor, courseid)

                get_profs(results, cursor, courseid)

                return results

    # Database cannot be opened
    except OperationalError as ex:
        # tell the client there was an error
        print("%s: " % argv[0], ex, file=stderr)
        send_error_to_client(ex, sock)
        return None

    # Database is corrupted
    except DatabaseError as ex:
        print("%s: " % argv[0], ex, file=stderr)
        send_error_to_client(ex, sock)
        return None

    # Class with class id does not exist
    except ValueError as ex:
        print(
            "no class with class id %s exists" % class_id, file=stderr
        )
        send_error_to_client(ex, sock)
        return None

    # Catch all other exceptions
    except Exception as ex:
        print("%s: " % argv[0], ex, file=stderr)
        exit(1)


# Tell the client if there's a DB error
def send_error_to_client(ex, sock):
    # confirm that the server has data for the client
    out_flo = sock.makefile(mode="wb")
    dump(False, out_flo)
    out_flo.flush()

    # Send the data to the client
    dump(ex, out_flo)
    out_flo.flush()


def handle_client(sock, delay):
    # Read data from the client
    in_flo = sock.makefile(mode="rb")
    client_data = load(in_flo)
    in_flo.close()

    # Artificial delay
    consume_cpu_time(delay)

    # Choose which DB query to use based on type of data from client
    server_data = None
    if isinstance(client_data, dict):
        print("Recieved command: get_overviews")
        server_data = get_overviews(client_data, sock)
    elif isinstance(client_data, str):
        print("Recieved command: get_detail")
        server_data = get_detail(client_data, sock)

    if server_data is not None:
        # confirm that the server does not have data for the client
        out_flo = sock.makefile(mode="wb")
        dump(True, out_flo)

        # Send an empty array to the client
        dump(server_data, out_flo)
        out_flo.flush()

    print("Closed socket")


def main():
    parsed_args = parse_args(argv)
    port = parsed_args["port"][0]
    delay = parsed_args["delay"][0]

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
                sock, _ = server_sock.accept()
                with sock:
                    print("Accepted connection, opened socket")
                    process = Process(
                        target=handle_client, args=[sock, delay]
                    )
                    process.start()

            except ConnectionError as ex:
                print("%s: " % argv[0], ex, file=stderr)
                exit(1)

            except Exception as ex:
                print(ex, file=stderr)
                exit(1)

    except ConnectionError as ex:
        print("%s: " % argv[0], ex, file=stderr)
        exit(1)

    except Exception as ex:
        print(ex, file=stderr)
        exit(1)


if __name__ == "__main__":
    main()
