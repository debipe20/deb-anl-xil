import time
import socket
import pandas as pd


def main():
    #load the CSV file
    input_file_path = 'UDDS-cycle_zero_grade.csv'

    host_ip = '127.0.0.1'  # Localhost
    host_port = 5000  # Port to listen on
    speed_data_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    speed_data_sender_socket.bind((host_ip, host_port))
    
    client_ip = '127.0.0.1'  # Localhost for the client
    client_port = 5001  # Port for the client to receive data
    
    while True:
        try:
            # Read the CSV file
            df = pd.read_csv(input_file_path)

            # Iterate through each row in the DataFrame
            for index, row in df.iterrows():
                # Extract speed and time from the row
                speed_mph = row['Speed (mph)']
                speed_mps = speed_mph * 0.44704
                time_stamp = row['Time (s)']

                # Create a message to send
                message = f"{time_stamp},{speed_mps}".encode('utf-8')

                # Send the message over UDP
                speed_data_sender_socket.sendto(message, (client_ip, client_port))

                # Print the sent message for debugging
                print(f"[{time.time()}]: Sent message is: {message.decode('utf-8')}")

                # Sleep for a short duration to simulate real-time sending
                time.sleep(0.1)

        except KeyboardInterrupt:
            speed_data_sender_socket.close()
            print("Speed data sender stopped.")
            break
    
    speed_data_sender_socket.close()
    
if __name__ == "__main__":
    main()