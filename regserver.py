#regserver.py
from sys import exit, argv, stderr
from socket import socket
from pickle import load, dump
from os import name

# query DB for all class rows that meet the parameters
def get_classes(class_info):
    print(class_info)

# query DB for all details of one class with id classid
def get_details(classid):
    print(classid)


def handle_client(sock):
    

    # Read data from the client
    in_flo = sock.makefile(mode="rb")
    client_data = load(in_flo)
    in_flo.close()

    if type(client_data) == dict:
        get_classes()
    elif type(client_data) == str:
        get_details()



    # Send the list of rows to the server
    out_flo = sock.makefile(mode="wb")
    dump(class_info, out_flo)
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
