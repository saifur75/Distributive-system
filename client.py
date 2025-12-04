 import socket
 BUF_SIZE = 8192
 PORT = 50000 # Change this if using university servers
 VERBOSE = True # Controls printing sent and received messages to the terminal, change to False to disable
 
 def receive()-> str:
    data = b''
    while True:
       try:
          part = sock.recv(BUF_SIZE)
       except (TimeoutError, socket.timeout):
           break
       data += part
       if len(part) < BUF_SIZE: # Check if reached end of message
          break
 
 message = data.decode().strip()
 if VERBOSE:
     print("Received:", message)
 
 return message
 def send(message: str):
     if VERBOSE:
        print("Sent:", message)
     sock.sendall(bytes(f"{message}\n", encoding="utf-8"))
 
 sock = socket.socket()
 sock.settimeout(2)
 sock.connect(("localhost", PORT))