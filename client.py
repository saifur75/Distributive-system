import socket
import sys

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 client.py <ip> <port>")
        sys.exit(1)

    IP = sys.argv[1]
    PORT = int(sys.argv[2])

    # Connect to server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP, PORT))

    # Send HELO handshake
    s.sendall("HELO\n".encode())

    # Receive server response
    data = s.recv(1024).decode().strip()
    if data != "OK":
        print("Unexpected response:", data)
        s.close()
        return

    # Ready for messages
    s.sendall("REDY\n".encode())

    while True:
        msg = s.recv(1024).decode().strip()
        if msg == "" or msg == "NONE":
            break

        parts = msg.split()

        # JOB message: JOBN submit_time job_id est_runtime core memory disk
        if parts[0] == "JOBN":
            job_id = parts[2]

            # Request list of servers
            s.sendall(f"GETS All\n".encode())

            data = s.recv(1024).decode().strip().split()
            if len(data) != 2 or data[0] != "DATA":
                break

            count = int(data[1])

            # Tell server we are ready
            s.sendall("OK\n".encode())

            # Read all server records
            servers = []
            for _ in range(count):
                rec = s.recv(1024).decode().strip()
                servers.append(rec)

            s.sendall("OK\n".encode())
            s.recv(1024).decode()

            # Choose first server
            first = servers[0].split()
            server_type = first[0]
            server_id = first[1]

            # Schedule job
            s.sendall(f"SCHD {job_id} {server_type} {server_id}\n".encode())

        elif parts[0] == "JCPL":
            s.sendall("REDY\n".encode())

        else:
            s.sendall("REDY\n".encode())

    # Quit
    s.sendall("QUIT\n".encode())
    s.close()

if __name__ == "__main__":
    main()
