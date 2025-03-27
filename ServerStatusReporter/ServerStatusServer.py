import socket
import json
import tkinter as tk
import threading

HOST = 'localhost'
PORT = 12345

def handle_client(conn, addr):
    print(f"Connected by {addr}")

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            message = data.decode('utf-8')
            print(f"Received: {message}")

            # Parse the JSON data
            try:
                parsed_data = json.loads(message)
                print(f"Parsed Data: {parsed_data}")

                # Print in a readable format
                print(f"Timestamp: {parsed_data['timestamp']}")
                print(f"Metric Name: {parsed_data['metric_name']}")
                print(f"Value: {parsed_data['value']}")

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")

    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        conn.close()
        print(f"Connection closed.")


#if __name__ == "__main__":
#    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#        s.bind((HOST, PORT))
#        s.listen()
#        print(f"Server listening on {HOST}:{PORT}")
#        while True:  # Infinite loop
#            conn, addr = s.accept()
#            handle_client(conn, addr)
            
#-------------------------------
#
# Tkinter gui build for server
#

def send_data (button_number):
     # Sends the button number to the client.
     try:
         message = json.dumps({'button_number': button_number})
         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
             s.connect((HOST, PORT))
             s.sendall(message.encode('UTF-8'))
     except Exception as e:
         print(f"Error sending data: {e}")
         
def run_socket_thread():
    # Runs the socket communication in a seperate thread.
    while True:
        send_data(1) # we will update this with better logic
        # add a short delay to avoid busy waiting
        # time.sleep(0.1)
    
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Server GUI")
    
    for i in range(1, 13):
        button = tk.Button(root, text=f"button {i}", command=lambda num=i: threading.Thread(target=lambda: send_data(num)).start())
        button.pack(pady=10)
        
    root.mainloop()





