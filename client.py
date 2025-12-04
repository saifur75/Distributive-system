import socket
import sys

USERNAME = "48600911"  # use your MQ OneID or required username


def send(sock, msg: str) -> None:
    """Send a single ds-sim command with newline."""
    sock.sendall((msg + "\n").encode())


def recv_line(sock) -> str:
    """
    Receive a single line (ending with '\n') from ds-server.
    Returns the line without the trailing newline.
    """
    data = ""
    while True:
        ch = sock.recv(1).decode()
        if ch == "":
            # connection closed
            break
        data += ch
        if ch == "\n":
            break
    return data.strip()


def get_all_servers(sock):
    """
    Send GETS All, parse DATA n recLen, read n server records,
    and return the list of server lines.
    """
    # Request server info
    send(sock, "GETS All")

    # Example: DATA 5 123
    header = recv_line(sock)
    parts = header.split()
    if len(parts) < 3 or parts[0] != "DATA":
        # Unexpected response
        return []

    n = int(parts[1])  # number of records

    # Acknowledge we're ready to receive the records
    send(sock, "OK")

    # Read n lines of server info as a batch
    data = ""
    while data.count("\n") < n:
        chunk = sock.recv(4096).decode()
        if chunk == "":
            break
        data += chunk

    # Split into lines and take first n records
    records = data.strip().split("\n")
    records = records[:n]

    # Tell server we're done reading the server list
    send(sock, "OK")

    # Read the '.' line from server
    _ = recv_line(sock)  # should be "."

    return records


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 client.py <ip> <port>")
        sys.exit(1)

    ip = sys.argv[1]
    port = int(sys.argv[2])

    # Connect to ds-server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))

    # ----- Handshake: HELO, AUTH, REDY -----
    send(s, "HELO")
    _ = recv_line(s)      # expect OK

    send(s, f"AUTH {USERNAME}")
    _ = recv_line(s)      # expect OK

    send(s, "REDY")

    # ----- Main simulation loop -----
    while True:
        msg = recv_line(s)
        if not msg:
            break

        parts = msg.split()
        cmd = parts[0]

        # Job arrived: schedule it
        if cmd == "JOBN" or cmd == "JOBP":
            # JOBN submitTime jobID estRuntime core memory disk
            job_id = parts[2]

            # Get all servers and pick the first one (simple baseline)
            servers = get_all_servers(s)
            if not servers:
                # If for some reason we didn't get any servers, just quit
                send(s, "QUIT")
                _ = recv_line(s)
                break

            first = servers[0].split()
            server_type = first[0]
            server_id = first[1]

            # Schedule the job
            send(s, f"SCHD {job_id} {server_type} {server_id}")
            _ = recv_line(s)  # expect OK

            # Ask for next event
            send(s, "REDY")

        # Job completion or other event: just ask for next one
        elif cmd in ("JCPL", "RESF", "RESR", "CHKQ"):
            send(s, "REDY")

        # No more jobs: terminate properly
        elif cmd == "NONE":
            send(s, "QUIT")
            _ = recv_line(s)  # server's final response
            break

        # Any other unexpected message: be safe and try to continue
        else:
            send(s, "REDY")

    s.close()


if __name__ == "__main__":
    main()
