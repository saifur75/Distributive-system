import socket

BUF_SIZE = 8192
PORT = 50000  # Change this if using university servers
VERBOSE = True  # Controls printing sent/received messages to terminal

def receive() -> str:
    data = b''
    while True:
        try:
            part = sock.recv(BUF_SIZE)
        except (TimeoutError, socket.timeout):
            break

        data += part

        # Check if end of message
        if len(part) < BUF_SIZE:
            break

    message = data.decode().strip()

    if VERBOSE:
        print("Received:", message)

    return message


def send(message: str):
    if VERBOSE:
        print("Sent:", message)

    sock.sendall(bytes(f"{message}\n", encoding="utf-8"))


# Socket setup
sock = socket.socket()
sock.settimeout(2)
sock.connect(("localhost", PORT))
