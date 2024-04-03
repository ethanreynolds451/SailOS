''' UI Layout

        Header

        Serial Port             Serial Baudrate            Address             Disconnected
        _______             ____________          _______
        _______             ____________          _______                 Connect



                                                            Buttons

        

                      Serial MonitorConsole                                            Console
      |                                                                          |       |                                                |
      |                                                                          |       |                                                |
      |                                                                          |       |                                                |
      |                                                                          |       |                                                |
      |                                                                          |       |                                                |

'''

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

# Commands
class Command:
    # Local
    transmisson_request = "RQTRANSMISSION="
    data_header = "DATA:"
    # Basic Control
    confirm = "CONFRM"
    response = "GTRESP"
    broadcast = "BRDCST"
    reset = "RESET"
    empty = "CMEMTY"
    fill = "CMFILL"
    stop = "CMSTOP"
    # Sensor Retrieval
    get_time = "GTTIME"
    get_pressure = "GTPRSS"
    # Data Transmission
    get_data_count = "GTDTCT"
    get_data = "GTDATA"
    get_sample_data = "GTSDTA"
    # Compound functions
    vertical_profile = "CMVPRO"
    down_up = "CMDNUP"
    center = "CMCNTR"

# Main Window Setup
defaultMainWindowSize = '800x600'
root = tk.Tk()
root.title("MATE Float")
root.geometry(defaultMainWindowSize)

# <editor-fold desc="Serial Setup">

#Serial Setup Variabes

transmit_buffer = ""
transmit_time = time.time()*1000
transmit_wait = 350
transmit_limit = 450
transmit_timeout = 1000
transmit_interval = 50

Float = serial.Serial()
Float.baudrate = 115200
Float.write_timeout = 0
ports = list()
Float_port = tk.StringVar(root)
Float_port.set("No Port Selected")
Float_baudrate = tk.StringVar(root)
Float_baudrate.set(Float.baudrate)
baud_options = [110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200, 128000, 256000]
Float_address = tk.StringVar(root)
def center_text(event):
    addressEntry.delete(0, tk.END)
    addressEntry.insert(0, str.center(addressEntry.get(), 3))
Float_address.set(1)
active_command = tk.StringVar(root)
active_command.set("Enter Commands Here")
command_send_status =  tk.StringVar(root)
command_send_status.set("No Message Sent")
connection_status = tk.StringVar(root)
connection_status.set("Disconnected")
active_message = ""
directory =  tk.StringVar(root)
directory.set(Path.home() / "Desktop")
# </editor-fold>

# <editor-fold desc="Core Functions">
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

def console_clear():
    console['state'] = 'normal'
    console.delete("1.0", "end")
    console['state'] = 'disabled'

def get_ports():
    global ports
    ports.clear()
    ports.append("No Port Selected")
    p = [tuple(p) for p in list(serial.tools.list_ports.comports())]
    for i in p:
        for x in i:
            if x != "n/a":
                # if "dev" in x: # THIS DOESNT WORK ON WINDOWS
                # Needed for serial on Mac - renames port so it can connect, but only if .cu is found
                x = re.sub(".cu.", "/tty.", x)
                ports.append(x)

def disconnect(*args):
    Float.close()
    connection_status.set("Disconnected")

def connect():
        #First, close the port if it is already open
        try:
            Float.close()
        except:
            pass
        #Then, attempt to connect to device with selected parameters
        try:
            Float.port = Float_port.get()
            Float.baudrate = Float_baudrate.get()
            Float.open()
            connection_status.set("Connected")
            console_println("*Device connected")
            console_println(" Port: "+str(Float.port))
            console_println(" Baudrate: "+str(Float.baudrate))
        except:
            disconnect()
            console_println("*Error opening serial port")
            console_println(" Port: "+str(Float.port))
            console_println(" Baudrate: "+str(Float.baudrate))

def serialMonitor_print(message):
    serialMonitor['state'] = 'normal'
    serialMonitor.insert(tk.END, message)
    serialMonitor['state'] = 'disabled'
    serialMonitor.yview_pickplace("end")

def serialMonitor_println(message):
    serialMonitor['state'] = 'normal'
    serialMonitor.insert(tk.END, "\n"+message)
    serialMonitor['state'] = 'disabled'
    serialMonitor.yview_pickplace("end")

def serialMonitor_clear():
    serialMonitor['state'] = 'normal'
    serialMonitor.delete("1.0", "end")
    serialMonitor['state'] = 'disabled'

def send(data):
    global transmit_buffer
    try:
        transmit_buffer = "AT+SEND=" + str(Float_address.get()) + "," + str(len(data)) + "," + data + bytes([0x0D, 0x0A]).decode()
    except:
        if not Float.isOpen():
            console_println("Serial device disconnected")
        else:
            console_println("Error writing to port")
        disconnect()

def sendCommand():
    send(active_command.get())

def com_print(message):
    communicationMonitor['state'] = 'normal'
    communicationMonitor.insert(tk.END, message)
    communicationMonitor['state'] = 'disabled'
    communicationMonitor.yview_pickplace("end")

def com_println(message):
    communicationMonitor['state'] = 'normal'
    communicationMonitor.insert(tk.END, "\n"+message)
    communicationMonitor['state'] = 'disabled'
    communicationMonitor.yview_pickplace("end")

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
        com_println(parse_message(data))

def read_serial():
    global transmit_time
    if Float.isOpen():
        try:
            if Float.inWaiting() > 0:
                transmit_time = time.time()*1000
                serialData = Float.readline().decode().rstrip()
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
        menu.add_command(label=port, command=lambda value=port: [Float_port.set(value), disconnect()])
    root.after(3000, update_ports)

def create_colored_frame(parent, row, span, color):
    frame = tk.Frame(parent, bg=color)
    frame.grid(row=row, column=0, rowspan=span, columnspan=Layout.maxWidth, sticky="nsew")
    return frame

def select_directory():
    directory.set(filedialog.askdirectory(initialdir=directory.get()))
    savePath['state'] = 'normal'
    savePath.delete("1.0","end")
    savePath.insert(tk.END, directory.get())
    savePath['state'] = 'disabled'

def get_data():
    ## Check to see if the float is ready to relay message
    if "RQTRANSMISSION" in active_message:
        ## Create a CSV file in selected directory to save data
        try:
            #Create folder path with date if it does not already exist
            main_directory = directory.get()
            print(main_directory)
            folder = main_directory+ "/Float_Data/" + str(datetime.now().date())+"/"
            # Creat container folder if it does not already exist
            if not os.path.exists(main_directory + "/Float_Data/"):
                os.mkdir(main_directory + "/Float_Data/")
             # Creat date folder if it does not already exist
            if not os.path.exists(folder):
                os.mkdir(folder)
            #Create CSV file with time in date directory
            file = folder + "/" + str(datetime.utcnow().strftime("%H:%M:%S")).replace(':','') + ".csv"
            console_println("Reading data from float...")
        except:
            console_println("Error creating file\nCheck folder permissions")

def transmit():
    global transmit_buffer
    try:
        if len(transmit_buffer) > 0:
            t = time.time()*1000 - transmit_time     # Time since last transmission recieved
            if t > transmit_wait and not transmit_limit < t < transmit_timeout:
                Float.write(transmit_buffer.encode())
                transmit_buffer = ""
    except:
        print("Something went Wrong!")
    root.after(transmit_interval, transmit)

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

# Grid

# UI Layout definitions
# Grid Layout Parameters

# </editor-fold>

# <editor-fold desc="UI Layout">
# Tkinter widget layout
class Layout:
    # <editor-fold desc="Header">
    maxWidth = 8
    maxHeight = 6
    headerRow = 0
    labelRow = 1
    selectorRow = 2
    portColumn = 0
    portColumnSpan = 4
    baudColumn = portColumnSpan
    baudColumnSpan = 1
    addressColumn = portColumnSpan + baudColumnSpan
    addressColumnSpan = 1
    connectionColumn = portColumnSpan + baudColumnSpan + addressColumnSpan
    connectionColumnSpan = 1
    # </editor-fold>

    # <editor-fold desc="Control panel">
    controlPanelRow = 3
    controlPanelRowSpan = 1

    verticalProfileRow = 0
    verticalProfileColumn = 0
    verticalProfileRowSpan = 2
    verticalProfileColumnSpan = 2

    upButtonRow = 0
    upButtonColumn = verticalProfileColumnSpan
    upButtonRowSpan = 1
    upButtonColumnSpan = 1

    downButtonRow = 0
    downButtonColumn = upButtonColumn + upButtonRowSpan
    downButtonRowSpan = 1
    downButtonColumnSpan = 1

    stopButtonRow = 1
    stopButtonColumn = verticalProfileColumnSpan
    stopButtonRowSpan = 1
    stopButtonColumnSpan = 2
    stopButtonWidth = 8
    stopButtonHeight = 1

    fillEmptyButtonRow = 0
    fillEmptyButtonColumn = stopButtonColumn + stopButtonColumnSpan
    fillEmptyButtonRowSpan = 1
    fillEmptyButtonColumnSpan = 2
    fillEmptyButtonWidth = 6
    fillEmptyButtonHeight = 1

    centerButtonRow = 1
    centerButtonColumn = stopButtonColumn + stopButtonColumnSpan
    centerButtonRowSpan = 1
    centerButtonColumnSpan = 2
    centerButtonWidth = 6
    centerButtonHeight = 1

    savePathRow = 0
    savePathColumn = fillEmptyButtonColumn + fillEmptyButtonColumnSpan
    savePathColumnSpan = 4

    directorySelectRow = savePathRow
    directorySelectColumn = savePathColumn + savePathColumnSpan
    directorySelectColumnSpan = 1

    getDataRow = 1
    getDataColumn = savePathColumn
    getDataRowSpan = 1
    getDataColumnSpan = savePathColumnSpan
    getDataWidth = 15
    getDataHeight = 1

    resetButtonRow = 1
    resetButtonColumn = directorySelectColumn
    resetButtonRowSpan = getDataRowSpan
    resetButtonColumnSpan = directorySelectColumnSpan
    # </editor-fold>

    # <editor-fold desc="Communication Panel">
    communicationPanelRow = controlPanelRow + controlPanelRowSpan
    communicationPanelRowSpan = maxWidth

    commandSendRow = 1
    commandSendRowSpan = 1
    commandSendColumn = 0
    commandSendColumnSpan = int(communicationPanelRowSpan / 2) - 2
    commandSendWidth = 20

    dataMonitorRow = commandSendRow + commandSendRowSpan
    dataMonitorRowSpan = 1
    dataMonitorColumn = commandSendColumn
    dataMonitorColumnSpan = int(communicationPanelRowSpan / 2)
    dataMonitorWidth = commandSendWidth
    dataMonitorHeight = 1

    serialMonitorRow = dataMonitorRow + dataMonitorRowSpan
    serialMonitorRowSpan = 1
    serialMonitorColumn = commandSendColumn
    serialMonitorColumnSpan = dataMonitorColumnSpan
    serialMonitorWidth = commandSendWidth
    serialMonitorHeight = 15

    commandSendButtonRow = commandSendRow
    commandSendButtonRowSpan = 1
    commandSendButtonColumn = commandSendColumn + commandSendColumnSpan
    commandSendButtonColumnSpan = 2
    commandSendButtonWidth = 8

    consoleRow = commandSendRow + commandSendRowSpan
    consoleRowSpan = serialMonitorRowSpan + commandSendButtonRowSpan
    consoleColumn = serialMonitorColumnSpan
    consoleColumnSpan = int(communicationPanelRowSpan / 2)
    consoleWidth = 30
    consoleHeight = 20

    clearButtonRow = commandSendRow
    clearButtonRowSpan = 1
    clearButtonColumn = consoleColumn
    clearButtonColumnSpan = 2
    clearButtonWidth = 8
    # </editor-fold>

# Fonts
class Fonts:
    headerFontSize = 32
    headerFontStyle = "Comic Sans"
    headerFontColor = "white"
    labelFontSize = 18
    labelFontStyle = "Comic Sans"
    labelFontColor = "black"
    selectorFontSize = 14
    selectorFontStyle = "Comic Sans"
    selectorFontColor = "black"

# Colors
class Colors:
    headerRowColor = "#2784CF"
    labelRowColor = "yellow"
    selectorRowColor = "orange"
    controlPanelRowColor = "red"
    communicationPanelColor = "#24BAD6"
    # Create colored backgrounds
    createHeaderColor = create_colored_frame(root, Layout.headerRow, 1, headerRowColor)
    createLabelColor = create_colored_frame(root, Layout.labelRow, 1, labelRowColor)
    createSelectorColor = create_colored_frame(root, Layout.selectorRow, 1, selectorRowColor)
    createControlPanelColor = create_colored_frame(root, Layout.controlPanelRow, 1, controlPanelRowColor)
    createCommandSendColor = create_colored_frame(root, Layout.communicationPanelRow, Layout.communicationPanelRowSpan, communicationPanelColor)

paddings = {'padx': 5, 'pady': 5}
# </editor-fold>

# <editor-fold desc="Tkinter Widgets">
# <editor-fold desc="Header">
# Header
headerLabel = tk.Label(root, text="Sound School Ocean Engineering", fg=Fonts.headerFontColor, font=(Fonts.headerFontStyle, Fonts.headerFontSize), justify='center', bg=Colors.headerRowColor)
headerLabel.grid(row=Layout.headerRow, column=0, columnspan=Layout.maxWidth, **paddings, sticky="ew")

# Port
portLabel = tk.Label(root, text="Serial Port", anchor='center', justify='center', fg=Fonts.labelFontColor, font=(Fonts.labelFontStyle, Fonts.labelFontSize), bg=Colors.labelRowColor)
portLabel.grid(row=Layout.labelRow, column=Layout.portColumn, columnspan=Layout.portColumnSpan, **paddings, sticky="ew")
portSelect = tk.OptionMenu(root, Float_port, "No Port Selected")
portSelect.config(width=15)
portSelect.grid(row=Layout.selectorRow, column=Layout.portColumn, columnspan=Layout.portColumnSpan, **paddings, sticky="ew")

# Baud
baudLabel = tk.Label(root, text="Baudrate", anchor='center', justify='center', fg=Fonts.labelFontColor, font=(Fonts.labelFontStyle, Fonts.labelFontSize), bg=Colors.labelRowColor)
baudLabel.grid(row=Layout.labelRow, column=Layout.baudColumn, columnspan=Layout.baudColumnSpan, **paddings, sticky="ew")
baudSelect = tk.OptionMenu(root, Float_baudrate, *baud_options)
Float_baudrate.trace("w", disconnect)
baudSelect.config(width=6)
baudSelect.grid(row=Layout.selectorRow, column=Layout.baudColumn, columnspan=Layout.baudColumnSpan, **paddings, sticky="ew")

# Address
addressLabel = tk.Label(root, text="Address", anchor='center', justify='center', fg=Fonts.labelFontColor, font=(Fonts.labelFontStyle, Fonts.labelFontSize), bg=Colors.labelRowColor)
addressLabel.grid(row=Layout.labelRow, column=Layout.addressColumn, columnspan=Layout.addressColumnSpan, **paddings, sticky="ew")
addressEntry = tk.Entry(root, textvariable=Float_address, justify="center", width=5)
addressEntry.bind("<FocusOut>", center_text)
addressEntry.grid(row=Layout.selectorRow, column=Layout.addressColumn, columnspan=Layout.addressColumnSpan, **paddings, sticky="ew")

# Connection
connectLabel = tk.Label(root, textvariable=connection_status, anchor='center', justify='center', fg=Fonts.labelFontColor, font=(Fonts.labelFontStyle, Fonts.labelFontSize), bg=Colors.labelRowColor)
connectLabel.grid(row=Layout.labelRow, column=Layout.connectionColumn, columnspan=Layout.connectionColumnSpan, **paddings, sticky="ew")
connectButton = tk.Button(root, text="Connect", command=connect, anchor='center', justify='center', fg=Fonts.selectorFontColor, font=(Fonts.selectorFontStyle, Fonts.selectorFontSize), bg=Colors.selectorRowColor)
connectButton.grid(row=Layout.selectorRow, column=Layout.connectionColumn, rowspan=1, columnspan=Layout.connectionColumnSpan, **paddings, sticky="ew")
# </editor-fold>

# <editor-fold desc="Control Panel">
controlPanel = tk.Frame(root, bg=Colors.controlPanelRowColor)
controlPanel.grid(row=Layout.controlPanelRow, column=0, rowspan=1, columnspan=Layout.maxWidth, **paddings, sticky="ew")

# Vertical Profile Command Shortcut
verticalProfile = tk.Button(controlPanel, text="Vertical Profile", width=15, height=4, command=lambda: send(Command.vertical_profile))
verticalProfile.grid(row=Layout.verticalProfileRow, column=Layout.verticalProfileColumn,
                     rowspan=Layout.verticalProfileRowSpan, columnspan=Layout.verticalProfileColumnSpan, **paddings,
                     sticky="ew")

# Up Button
upButton = tk.Button(controlPanel, text="Up", width=4, height=1, command=lambda: send(Command.empty))
upButton.grid(row=Layout.upButtonRow, column=Layout.upButtonColumn, rowspan=Layout.upButtonRowSpan,
              columnspan=Layout.upButtonColumnSpan, **paddings, sticky="ew")

# Down Button
downButton = tk.Button(controlPanel, text="Down", width=4, height=1, command=lambda: send(Command.fill))
downButton.grid(row=Layout.downButtonRow, column=Layout.downButtonColumn, rowspan=Layout.downButtonRowSpan,
                columnspan=Layout.downButtonColumnSpan, **paddings, sticky="ew")

# Stop Button
stopButton = tk.Button(controlPanel, text="Stop", width=Layout.stopButtonWidth, height=Layout.stopButtonHeight, command=lambda: send(Command.stop))
stopButton.grid(row=Layout.stopButtonRow, column=Layout.stopButtonColumn, rowspan=Layout.stopButtonRowSpan,
                columnspan=Layout.stopButtonColumnSpan, **paddings, sticky="ew")

# Up and Down (fill then empty)
fillEmptyButton = tk.Button(controlPanel, text="Down / Up", width=Layout.fillEmptyButtonWidth, height=Layout.fillEmptyButtonHeight, command=lambda: send(Command.down_up))
fillEmptyButton.grid(row=Layout.fillEmptyButtonRow, column=Layout.fillEmptyButtonColumn, rowspan=Layout.fillEmptyButtonRowSpan, columnspan=Layout.fillEmptyButtonColumnSpan, **paddings, sticky="ew")

# Move to center
centerButton = tk.Button(controlPanel, text="Center", width=Layout.centerButtonWidth, height=Layout.centerButtonHeight, command=lambda: send(Command.center))
centerButton.grid(row=Layout.centerButtonRow, column=Layout.centerButtonColumn, rowspan=Layout.centerButtonRowSpan, columnspan=Layout.centerButtonColumnSpan, **paddings, sticky="ew")

# File Path
savePath = tk.Text(controlPanel, width=30, height=1)
savePath.grid(row=Layout.savePathRow, column=Layout.savePathColumn, rowspan=1, columnspan=Layout.savePathColumnSpan,
              **paddings, sticky="ew")
savePath.insert(tk.END, directory.get())
savePath['state'] = 'disabled'

# File Path Select
directorySelect = tk.Button(controlPanel, text="Select", anchor='center', justify='center',
                            command=lambda: select_directory())
directorySelect.grid(row=Layout.directorySelectRow, column=Layout.directorySelectColumn, rowspan=1,
                     columnspan=Layout.directorySelectColumnSpan, **paddings, sticky="ew")

# Get Data
getData = tk.Button(controlPanel, width=Layout.getDataWidth, height=Layout.getDataHeight, text="Retrieve Data",
                    anchor='center', justify='center', command=lambda: get_data())
getData.grid(row=Layout.getDataRow, column=Layout.getDataColumn, rowspan=Layout.getDataRowSpan,
             columnspan=Layout.getDataColumnSpan, **paddings, sticky="ew")

resetButton = tk.Button(controlPanel, text="Reset", anchor='center', justify='center', command=lambda: send(Command.reset))
resetButton.grid(row=Layout.resetButtonRow, column=Layout.resetButtonColumn, rowspan=1,
                     columnspan=Layout.resetButtonColumnSpan, **paddings, sticky="ew")

controlPanel.grid_rowconfigure(0, weight=1)
controlPanel.grid_columnconfigure(0, weight=1)
# </editor-fold>

# <editor-fold desc="Communication Panel">
communicationPanel = tk.Frame(root, bg=Colors.communicationPanelColor)
communicationPanel.grid(row=Layout.communicationPanelRow, column=0, rowspan=Layout.communicationPanelRowSpan, columnspan=Layout.maxWidth, **paddings, sticky="ew")

# Command Send Bar
commandSend = tk.Entry(communicationPanel, textvariable=active_command, width=Layout.commandSendWidth)
commandSend.grid(row=Layout.commandSendRow, column=Layout.commandSendColumn, rowspan=Layout.commandSendRowSpan, columnspan=Layout.commandSendColumnSpan, **paddings,
                 sticky="ew")

# Command Send Button
commandSendButton = tk.Button(communicationPanel, text="Send", width=Layout.commandSendButtonWidth, bg=Colors.communicationPanelColor, command=sendCommand)
commandSendButton.grid(row=Layout.commandSendButtonRow, column=Layout.commandSendButtonColumn, rowspan=Layout.commandSendButtonRowSpan, columnspan=Layout.commandSendButtonColumnSpan, **paddings, sticky="ew")

# Communication Monitor
communicationMonitor = tk.Text(communicationPanel, width=Layout.dataMonitorWidth, height=Layout.dataMonitorHeight, padx=15, pady=15)
communicationMonitor.grid(row=Layout.dataMonitorRow, column=Layout.dataMonitorColumn, rowspan=Layout.dataMonitorRowSpan, columnspan=Layout.dataMonitorColumnSpan,
                          **paddings, sticky="ew")
communicationMonitor.insert(tk.END, "Float Messages")
communicationMonitor['state'] = 'disabled'

# Serial Monitor
serialMonitor = tk.Text(communicationPanel, width=Layout.serialMonitorWidth, height=Layout.serialMonitorHeight, padx=15, pady=15)
serialMonitor.grid(row=Layout.serialMonitorRow, column=Layout.serialMonitorColumn, rowspan=Layout.serialMonitorRow, columnspan=Layout.serialMonitorColumnSpan, **paddings, sticky="ew")
serialMonitor.insert(tk.END, "Serial Monitor")
serialMonitor['state'] = 'disabled'

# Console
console = tk.Text(communicationPanel, width=Layout.consoleWidth, height=Layout.consoleHeight, padx=15, pady=15)
console.grid(row=Layout.consoleRow, column=Layout.consoleColumn, rowspan=Layout.consoleRowSpan,
             columnspan=Layout.consoleColumnSpan, **paddings, sticky="ew")
console.insert(tk.END, "Console")
console['state'] = 'disabled'

# Clear Button
clearButton = tk.Button(communicationPanel, text="Clear", width=Layout.clearButtonWidth, bg=Colors.communicationPanelColor, command=lambda: [console_clear(),serialMonitor_clear()])
clearButton.grid(row=Layout.clearButtonRow, column=Layout.clearButtonColumn, rowspan=Layout.clearButtonRowSpan, columnspan=Layout.clearButtonColumnSpan, **paddings, sticky="ew")

communicationPanel.grid_rowconfigure(0, weight=1)
communicationPanel.grid_columnconfigure(0, weight=1)
# </editor-fold>

#Set window properties
root.grid_rowconfigure(Layout.maxHeight, weight=1)
root.grid_columnconfigure(Layout.portColumn, weight=1)
# </editor-fold>

# Begin interval functions
update_ports()
read_serial()
transmit()

# Execute Tkinter
root.mainloop()
