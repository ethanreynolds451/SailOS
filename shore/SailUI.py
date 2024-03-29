#-*- coding: utf-8 -*-

import time
import os
import tkinter as tk
from tkinter import *
import serial
import time
from datetime import datetime
import serial.tools.list_ports
import re
from tkinter import filedialog
from pathlib import Path
from tkinter import ttk
from tkinter import messagebox

# 13 inch Mac Book Pro with zoomed display (might figure out how to make adaptive later)
defaultMainWindowSize = '1024x640'

# Create main root window
root = tk.Tk()
root.title("SailboatUI")
root.geometry(defaultMainWindowSize)

#Serial Setup Variabes
boat = serial.Serial()
boat.baudrate = 9600
boat.write_timeout = 0
ports = list()

# Tkinter string variables for serial
boat_port = tk.StringVar(root)
boat_port.set("No Port Selected")
boat_baudrate = tk.StringVar(root)
boat_baudrate.set(boat.baudrate)
baud_options = [110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200, 128000, 256000]
boat_address = tk.StringVar(root)
boat_address.set(1)
connection_status = tk.StringVar(root)
connection_status.set("Disconnected")

# Tkinter string variables for communication
command_send = tk.StringVar(root)
command_send.set("Enter Commands Here")
command_send_status =  tk.StringVar(root)
command_send_status.set("No Message Sent")
active_message = ""
directory =  tk.StringVar(root)
directory.set(Path.home() / "Desktop")

# General use functions
def map_range(value, input_min, input_max, output_min, output_max):
    input_range = input_max - input_min
    output_range = output_max - output_min
    scaled_value = (value - input_min) / input_range
    mapped_value = output_min + (scaled_value * output_range)
    return mapped_value
def get_cardinal_direction(degrees):
    if 0 <= degrees <= 22.5 or 337.5 <= degrees <= 360:
        return "N"
    elif 22.5 < degrees <= 67.5:
        return "NE"
    elif 67.5 < degrees <= 112.5:
        return "E"
    elif 112.5 < degrees <= 157.5:
        return "SE"
    elif 157.5 < degrees <= 202.5:
        return "S"
    elif 202.5 < degrees <= 247.5:
        return "SW"
    elif 247.5 < degrees <= 292.5:
        return "W"
    elif 292.5 < degrees <= 337.5:
        return "NW"
    else:
        return "XX"  # Handle any other cases

# Icon class
class Icon:
    icon_directory = "Resources"
    disconnected = icon_directory + "/"  + "Connect_Icon@2x.png"
    connected =  icon_directory + "/"  + "Disconnect_Icon@2x.png"
    save = icon_directory + "/"  + "SaveFile_Icon@3x.png"
    start_log =  icon_directory + "/"  + "StartRecordingsmall_Icon@3x.png"
    end_log =  icon_directory + "/"  + "StopRecordingsmall_Icon@3x.png"
    clear =  icon_directory + "/"  + "Clearsmall_Icon@3x.png"

# Tkinter string variables for data display
class Dashboard:
    class InternalTemp:
        value = None
        string = tk.StringVar(root)
        string.set("-- °C")
        @classmethod
        def set(cls, x):
            cls.value = x
            cls.string.set(str(x) + " °C")
    class InternalMoisture:
        value = None
        string = tk.StringVar(root)
        string.set("-- %")
        @classmethod
        def set(cls, x):
            cls.value = x
            cls.string.set(str(x) + " %")
    class SailAngle:
        center = 110
        center_offset = 10
        degree_range = 220
        value = None
        tack = None
        string = tk.StringVar(root)
        string.set("-- °")
        @classmethod
        def set(cls, x):
            cls.value = map_range(x, 0, 1023, 0, degree_range)
            if cls.value > center + center_offset:
                cls.tack = "P"
            elif cls.value < center - center_offset:
                cls.tack = "S"
            else:
                cls.tack = "C"
            cls.string.set(str(x) + " ° " + cls.tack)
    class Heading:
        value = None
        cardinal = None
        string = tk.StringVar(root)
        string.set("---°   ---")
        def set(cls, x):
            cls.value = x
            cls.cardinal = get_cardinal_direction(x)
            cls.string.set(str(x) + " ° " + cls.cardinal)
    class Coordinates:
        lat = None
        long = None
        string = tk.StringVar()
        string.set("--° N, ---°W")
        def set(cls, lat, long):
            cls.lat = lat
            cls.long = long
            cls.string.set(str(lat) + "° N, " + str(long) + "° W")
    class WindDirection:
        # Wind sensor not designed
        value = None
        string =  tk.StringVar()
        string.set("---")
        def set(cls, x):
            cls.value = "XX"
        
#High Level UI Functions        
def console_print(message):
    console['state'] = 'normal'
    console.insert(tk.END, message)
    console['state'] = 'disabled'
    console.yview_pickplace("end")

def console_println(message):
    console['state'] = 'normal'
    console.insert(tk.END, "\n"+message)
    console['state'] = 'disabled'
    console.yview_pickplace("end")

# Serial Connection Functions
def get_ports():
    global ports
    ports.clear()
    ports.append("No Port Selected")
    p = [tuple(p) for p in list(serial.tools.list_ports.comports())]
    for i in p:
        for x in i:
            if x != "n/a":
                if "dev" in x:
                    x = re.sub(".cu.", "/tty.", x)
                    ports.append(x)

def disconnect(*args):
    boat.close()
    connection_status.set("Disconnected")

def connect():
        #First, close the port if it is already open
        try:
            boat.close()
        except:
            pass
        #Then, attempt to connect to device with selected parameters
        try:
            boat.port = boat_port.get()
            boat.baudrate = boat_baudrate.get()
            boat.open()
            connection_status.set("Connected")
            console_println("*Device connected")
            console_println(" Port: "+str(boat.port))
            console_println(" Baudrate: "+str(boat.baudrate))
        except:
            disconnect()
            console_println("*Error opening serial port")
            console_println(" Port: "+str(boat.port))
            console_println(" Baudrate: "+str(boat.baudrate))

def send(data):
    try:
        boat.write("AT+SEND=".encode())
        boat.write(boat_address.get().encode())
        boat.write(",".encode())
        boat.write(str(len(data)).encode())
        boat.write(",".encode())
        boat.write(data.encode())
        boat.write(bytes([0x0D, 0x0A]))
    except:
        if not boat.isOpen():
            console_println("Serial device disconnected")
        else:
            console_println("Error writing to port")
        disconnect()

#+RCV=1,23,Hello World: Seconds = ,-61,11
def parse_message(data):
    global active_message
    try:
        start = data.find(",", data.find(",") + 1)
        end = data.rfind(",",  0, data.rfind(",") )
        message = data[start + 1 : end]
        active_message = message
        return message
    except:
        console_println("Invalid Data")

def process_message(data):
    if  "+OK" in data:
        console_println("Send sucessful")
    if "+RCV" in data:
        console_println(parse_message(data))

def read_serial():
    if boat.isOpen():
        try:
            if boat.inWaiting() > 0:
                serialData = boat.readline().decode().rstrip()
                serialMonitor_println(serialData)
                process_message(serialData)
        except OSError or serial.SerialException:
            console_println("Serial device disconnected")
            disconnect()
        except Exception as e:
            console_println("Read error: {}".format(e))
    root.after(100, read_serial)

def update_ports():
    menu = portSelect["menu"]
    menu.delete("0",tk.END)
    get_ports()
    for port in ports:
        menu.add_command(label=port, command=lambda value=port: [boat_port.set(value), disconnect()])
    root.after(3000, update_ports)

def update_time():
    localtime = time.strftime("%H:%M:%S", time.localtime())
    timeDisplay.config(text=localtime)
    root.after(1000, update_time)

# Data log management
def select_directory():
    directory.set(filedialog.askdirectory(initialdir=directory.get()))
    savePath['state'] = 'normal'
    savePath.delete("1.0","end")
    savePath.insert(tk.END, directory.get())
    savePath['state'] = 'disabled'

##def get_data():
##    ## Check to see if the float is ready to relay message
##    if "RQTRANSMISSION" in active_message:
##        ## Create a CSV file in selected directory to save data
##        try:
##            #Create folder path with date if it does not already exist
##            main_directory = directory.get()
##            print(main_directory)
##            folder = main_directory+ "/Float_Data/" + str(datetime.now().date())+"/"
##            # Creat container folder if it does not already exist
##            if not os.path.exists(main_directory + "/Float_Data/"):
##                os.mkdir(main_directory + "/Float_Data/")
##             # Creat date folder if it does not already exist
##            if not os.path.exists(folder):
##                os.mkdir(folder)
##            #Create CSV file with time in date directory
##            file = folder + "/" + str(datetime.utcnow().strftime("%H:%M:%S")).replace(':','') + ".csv"
##            console_println("Reading data from float...")
##        except:
##            console_println("Error creating file\nCheck folder permissions")
##            
##        #Open the file and add a header
##        with open(file, 'w') as file:
##            try:
##                 
##
##
##            
##            try:
##                data_length = int(active_message[str.find(command.transmisson_request)+len(command.transmisson_request)+1:])
##                while(data_length > 0):
##                    if data_header in active_message:
##                        
##                console_println("Float data read sucessfully")
##                Float.write("GTDATA".encode())
##            except:
##                console_println("Failed to read data")
##    else:
##        console_println("No data to read")

# Tkinter UI functions
def create_colored_frame(parent, row, color):
    frame = tk.Frame(parent, bg=color)
    frame.grid(row=row, column=0, columnspan=maxWidth, sticky="nsew")
    return frame

#Grid layout dimensions
maxWidth = 12
maxHeight=12

# Assign top row for general tools
toolbarRow = 0

# Position time widget in top left toolbar
timeRow = toolbarRow
timeColumn = 0
timeColumnSpan = 2

# Position serial port selector after time in toolbar
portRow = toolbarRow
portColumn = 0 + timeColumnSpan
portColumnSpan = 3
portWidth = 15

# Position baud rate seletor after serial port selector in toolbar
baudRow = toolbarRow
baudColumn = portColumn + portColumnSpan
baudColumnSpan = 2
baudWidth = 6

# Position address entry after  baud rate selector in toolbar
addressRow = toolbarRow
addressColumn = baudColumn + baudColumnSpan
addressColumnSpan = 1
addressWidth = 5

# Position connect button after address entry in toolbar
connectRow = toolbarRow
connectColumn = addressColumn + addressColumnSpan
connectColumnSpan = 1
connectWidth = 5
connectHeight = 15

# Position log directory after connect button in toolbar
directoryRow = toolbarRow
directroyColumn = connectColumn + connectColumnSpan
directoryColumnSpan = 1

# Position start log after log directory in toolbar
logRow = toolbarRow
logColumn = directroyColumn + directoryColumnSpan
logColumnSpan = 1

# Position map widget below toolbar to the left
mapRow = toolbarRow + 1
mapRowSpan = 4
mapColumn = 0
mapColumnSpan = int(maxWidth / 2)

# Position dashboard container below toolbar to the right
dashboardRow = toolbarRow + 1
dashboardRowSpan = 4
dashboardColumn = mapColumn + mapColumnSpan
dashboardColumnSpan = int(maxWidth / 2)

# Position console on bottom left
consoleRow = mapRow + mapRowSpan
consoleColumn = 0
consoleColumnSpan = int(maxWidth / 2)
consoleRowSpan = 3
consoleWidth = 5
consoleHeight = 10

# Position control panel container on bottom right
controlRow = dashboardRow + dashboardRowSpan
controlRowSpan = 3
controlColumn = consoleColumn + consoleColumnSpan
controlColumnSpan =int( maxWidth / 2)

#Fonts
headerFontSize = 32
headerFontStyle = "Comic Sans"
headerFontColor = "red"
labelFontSize = 18
labelFontStyle = "Comic Sans"
labelFontColor = "orange"
selectorFontSize = 14
selectorFontStyle = "Comic Sans"
selectorFontColor = "black"


#Colors
headerRowColor =  "yellow"
labelRowColor =  "#24BAD6"
selectorRowColor = "#24BAD6"
controlPanelRowColor = "#2784CF"
commandSendRowColor = "orange"
consoleRowColor = "red"

paddings = {'padx': 5, 'pady': 5}

#Create colored backgrounds
# consoleColor = create_colored_frame(root, serialMonitorRow, consoleRowColor)

#Header
# headerLabel =  tk.Label(root, text="Sound School", fg=headerFontColor, font=(headerFontStyle, headerFontSize),justify='center', bg=headerRowColor)
# headerLabel.grid(row=headerRow, column=0, columnspan=maxWidth, sticky="ew", **paddings)

# Time Display
timeDisplay= tk.Label(root, text=time.strftime("%H:%M:%S", time.localtime()))
timeDisplay.grid(row=timeRow, column=timeColumn, columnspan=timeColumnSpan, **paddings)

#Port
portSelect = tk.OptionMenu(root, boat_port, "No Port Selected")
portSelect.config(width=portWidth)
portSelect.grid(row=portRow, column=portColumn, columnspan=portColumnSpan, sticky="ew", **paddings)

#Baud
baudSelect = tk.OptionMenu(root, boat_baudrate,  *baud_options)
boat_baudrate.trace("w", disconnect)
baudSelect.config(width=baudWidth)
baudSelect.grid(row=baudRow, column=baudColumn, columnspan=baudColumnSpan,  sticky="ew", **paddings)

#Address
addressEntry = tk.Entry(root, textvariable=boat_address, justify="center", width=addressWidth)
addressEntry.grid(row=addressRow, column=addressColumn, columnspan=addressColumnSpan, sticky="ew", **paddings)

# Connect
connectImage = tk.PhotoImage(file=Icon.disconnected)
connectButton = tk.Label(root, image=connectImage, width=connectWidth, height=connectHeight, anchor='center', justify='center', fg=selectorFontColor, font=(selectorFontStyle, selectorFontSize),bg=selectorRowColor)
connectButton.grid(row=connectRow, column = connectColumn, columnspan=connectColumnSpan, sticky="ew", **paddings)
connectButton.bind("<Button-1>", lambda event: connect())


#######################################################

# Map


#######################################################

# Dashboard

dashboard = tk.Frame(root, bg=controlPanelRowColor)
dashboard.grid(row=dashboardRow, column=dashboardColumn, rowspan=dashboardRowSpan, columnspan=dashboardColumnSpan, sticky="ew", **paddings)

dashboard.grid_rowconfigure(0, weight=1)
dashboard.grid_columnconfigure(0, weight=1)


#######################################################

# Console
console = tk.Text(root, width=consoleWidth, height=consoleHeight,  padx=15, pady=15)
console.grid(row=consoleRow, column=consoleColumn, rowspan=consoleRowSpan, columnspan=consoleColumnSpan, sticky="ew", **paddings)
console.insert(tk.END, "Console")
console['state'] = 'disabled'

#######################################################

# Control Panel

controlPanel = tk.Frame(root, bg=controlPanelRowColor)
controlPanel.grid(row=controlRow, column=controlColumn, rowspan=controlRowSpan, columnspan=controlColumnSpan, sticky="ew", **paddings)

dashboard.grid_rowconfigure(0, weight=1)
dashboard.grid_columnconfigure(0, weight=1)

#######################################################

# Other Stuff

##savePath = tk.Text(dashboard, width=30, height=1)
##savePath.grid(row=savePathRow, column=savePathColumn, rowspan=1, columnspan=savePathColumnSpan, sticky="ew",**paddings)
##savePath.insert(tk.END, directory.get())
##savePath['state'] = 'disabled'

#######################################################

#Set window properties
root.grid_rowconfigure(maxHeight, weight=1)
root.grid_columnconfigure(portColumn, weight=1)

update_ports()
update_time()
read_serial()

# Execute Tkinter
root.mainloop()
