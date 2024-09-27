# import serial

# # Define the serial port
# PORT = "COM1"
# BAUDRATE = 115200


# mySerial = serial.Serial(
#     port=PORT,
#     baudrate=BAUDRATE,
#     parity=serial.PARITY_NONE,
#     stopbits=serial.STOPBITS_ONE,
#     bytesize=serial.EIGHTBITS,
#     timeout=0.09,
# )


# while True:
#     data_received = mySerial.readline()
#     if len(data_received) > 0:
#         print("Data recevied: ", data_received)


import serial

# Define the serial port
PORT = "COM7"
BAUDRATE = 115200

# Set up the serial connection
mySerial = serial.Serial(
    port=PORT,
    baudrate=BAUDRATE,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=0.09,
)

while True:
    # Read data from the serial port
    data_received = mySerial.readline()

    # Check if data is received
    if len(data_received) > 0:
        try:
            # Decode the byte data to a UTF-8 string
            decoded_data = data_received.decode("utf-8").strip()
            print("Data received: ", decoded_data)
        except UnicodeDecodeError:
            print("Received data cannot be decoded to UTF-8")
