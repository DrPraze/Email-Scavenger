import socket

def main():
    host = '127.0.0.1'
    port = 12345

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    print("[*] Connected to server")

    while True:
        message = input("Enter a message (type 'exit' to quit): ")
        if message == 'exit':
            break

        # Send the message to the server
        client_socket.send(message.encode('utf-8'))

        # Receive and print the processed result from the server
        result = client_socket.recv(1024).decode('utf-8')
        print(f"Server says: {result}")

    client_socket.close()

if __name__ == "__main__":
    main()
  
