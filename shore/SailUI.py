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
from PIL import Image, ImageTk
import pygame
from pygame.locals import *

class SailUI(tk.Tk):
    def __init__(self):
        super().__init__()
        # Main window setuo
        self.title("SailboatUI")
        self.geometry('1024x640')   # 13 inch Mac Book Pro with zoomed display (might figure out how to make adaptive later)
        # Serial Setup Variabes
        self.device = serial.Serial()
        self.device.baudrate = 9600
        self.write_timeout = 0
        self.ports = list()
        # Tkinter string variables for serial
        self.selected_port = tk.StringVar(value="No Port Selected")
        self.selected_baudrate = tk.StringVar(value=str(self.device.baudrate))
        self.baud_options = [110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200, 128000, 256000]
        self.selected_address = tk.StringVar(value="1")
        self.connection_status = tk.StringVar(value="Disconnected")
        # Tkinter string variables for communication
        self.command_active = tk.StringVar(value="Enter Commands Here")
        self.command_send_status =  tk.StringVar(self)
        self.command_send_status.set("No Message Sent")
        self.active_message = ""
        self.directory =  tk.StringVar(self)
        self.directory.set(Path.home() / "Desktop")

        # Tkinter string variables for data display
        class Dashboard:
            class InternalTemp:
                value = None
                string = tk.StringVar(value="-- °C")

                @classmethod
                def set(cls, x):
                    cls.value = x
                    cls.string.set(str(x) + " °C")

            class InternalMoisture:
                value = None
                string = tk.StringVar(value="-- %")

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
                string = tk.StringVar(value="-- °")

                @classmethod
                def set(cls, x):
                    cls.value = SailUI.map_range(x, 0, 1023, 0, cls.degree_range)
                    if cls.value > cls.center + cls.center_offset:
                        cls.tack = "P"
                    elif cls.value < cls.center - cls.center_offset:
                        cls.tack = "S"
                    else:
                        cls.tack = "C"
                    cls.string.set(str(x) + " ° " + cls.tack)

            class Heading:
                value = None
                cardinal = None
                string = tk.StringVar(value="---°   ---")

                def set(cls, x):
                    cls.value = x
                    cls.cardinal = SailUI.get_cardinal_direction(x)
                    cls.string.set(str(x) + " ° " + cls.cardinal)

            class Coordinates:
                lat = None
                long = None
                string = tk.StringVar(value="--° N, ---°W")

                def set(cls, lat, long):
                    cls.lat = lat
                    cls.long = long
                    cls.string.set(str(lat) + "° N, " + str(long) + "° W")

            class WindDirection:
                # Wind sensor not designed
                value = None
                string = tk.StringVar(value="---")

                def set(cls, x):
                    cls.value = "XX"

        self.init_pygame()
        self.create_widgets()
        self.start()

    def init_pygame(self):
        pygame.init()
        self.screen = pygame.Surface((400, 300))
        pygame.display.set_caption('Pygame in Tkinter')
        self.pygame_label = tk.Label(self)
        self.pygame_label.grid(row=self.Layout.mapRow, column=self.Layout.mapColumn)

    def update_pygame(self):
        # Handle Pygame events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
            # Handle other Pygame events here

        # Update Pygame display
        self.screen.fill((255, 255, 255))
        pygame.draw.circle(self.screen, (255, 0, 0), (200, 150), 50)

        # Convert Pygame surface to a PIL image
        img = Image.frombytes('RGB', self.screen.get_size(), pygame.image.tostring(self.screen, 'RGB'))

        # Convert PIL image to a Tkinter-compatible format
        img_tk = ImageTk.PhotoImage(image=img)

        # Update the label with the new image
        self.pygame_label.configure(image=img_tk)
        self.pygame_label.image = img_tk

        # Call this function again after a short delay
        self.after(30, self.update_pygame)

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

    #High Level UI Functions
    def console_print(self, message):
        self.console['state'] = 'normal'
        self.console.insert(tk.END, message)
        self.console['state'] = 'disabled'
        self.console.yview_pickplace("end")

    def console_println(self, message):
        self.console['state'] = 'normal'
        self.console.insert(tk.END, "\n"+message)
        self.console['state'] = 'disabled'
        self.console.yview_pickplace("end")

    # Serial Connection Functions
    def get_ports(self):
        global ports
        self.ports.clear()
        self.ports.append("No Port Selected")
        p = [tuple(p) for p in list(serial.tools.list_ports.comports())]
        for i in p:
            for x in i:
                if x != "n/a":
                    if "dev" in x:
                        x = re.sub(".cu.", "/tty.", x)
                        self.ports.append(x)

    def disconnect(self, *args):
        self.device.close()
        self.connection_status.set("Disconnected")

    def connect(self):
            #First, close the port if it is already open
            try:
                self.device.close()
            except:
                pass
            #Then, attempt to connect to device with selected parameters
            try:
                self.device.port = self.selected_port.get()
                self.device.baudrate = self.selected_baudrate.get()
                self.device.open()
                self.connection_status.set("Connected")
                self.console_println("*Device connected")
                self.console_println(" Port: "+str(self.device.port))
                self.console_println(" Baudrate: "+str(self.device.baudrate))
            except:
                self.disconnect()
                self.console_println("*Error opening serial port")
                self.console_println(" Port: "+str(self.device.port))
                self.console_println(" Baudrate: "+str(self.device.baudrate))

    def send(self, data):
        try:
            self.device.write("AT+SEND=".encode())
            self.device.write(self.selected_address.get().encode())
            self.device.write(",".encode())
            self.device.write(str(len(data)).encode())
            self.device.write(",".encode())
            self.device.write(data.encode())
            self.device.write(bytes([0x0D, 0x0A]))
        except:
            if not self.device.isOpen():
                self.console_println("Serial device disconnected")
            else:
                self.console_println("Error writing to port")
            self.disconnect()

    #+RCV=1,23,Hello World: Seconds = ,-61,11
    def parse_message(self, data):
        global active_message
        try:
            start = data.find(",", data.find(",") + 1)
            end = data.rfind(",",  0, data.rfind(",") )
            message = data[start + 1 : end]
            self.active_message = message
            return message
        except:
            self.console_println("Invalid Data")

    def process_message(self, data):
        if  "+OK" in data:
            self.console_println("Send sucessful")
        if "+RCV" in data:
            self.console_println(self.parse_message(data))

    def read_serial(self):
        if self.device.isOpen():
            try:
                if self.device.inWaiting() > 0:
                    serialData = self.device.readline().decode().rstrip()
                    self.serialMonitor_println(serialData)
                    self.process_message(serialData)
            except OSError or serial.SerialException:
                self.console_println("Serial device disconnected")
                self.disconnect()
            except Exception as e:
                self.console_println("Read error: {}".format(e))
        self.after(100, self.read_serial)

    def update_ports(self):
        menu = self.portSelect["menu"]
        menu.delete("0",tk.END)
        self.get_ports()
        for port in self.ports:
            menu.add_command(label=port, command=lambda value=port: [self.selected_port.set(value), self.disconnect()])
        self.after(3000, self.update_ports)

    def update_time(self):
        localtime = time.strftime("%H:%M:%S", time.localtime())
        self.timeDisplay.config(text=localtime)
        self.after(1000, self.update_time)

    # Data log management
    def select_directory(self):
        self.directory.set(filedialog.askdirectory(initialdir=self.directory.get()))
        self.savePath['state'] = 'normal'
        self.savePath.delete("1.0","end")
        self.savePath.insert(tk.END, self.directory.get())
        self.savePath['state'] = 'disabled'

    # Tkinter UI functions
    def create_colored_frame(self, parent, row, color):
        frame = tk.Frame(parent, bg=color)
        frame.grid(row=row, column=0, columnspan=self.Layout.maxWidth, sticky="nsew")
        return frame

    # Icon class
    class Icon:
        default_image_data = b'GIF89a\x01\x00\x01\x00\x80\x01\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02L\x01\x00;'
        icon_directory = "Resources"
        disconnected = icon_directory + "Connect_Icon@2x.png"
        connected = icon_directory + "/"  + "Disconnect_Icon@2x.png"
        start_log = icon_directory + "/"  + "StartRecordingsmall_Icon@3x.png"
        end_log = icon_directory + "/"  + "StopRecordingsmall_Icon@3x.png"
        clear = icon_directory + "/"  + "Clearsmall_Icon@3x.png"
        save = icon_directory + "/"  + "SaveFile_Icon@3x.png"

        def load_image(self, file_path):
            if Path(file_path).exists():
                # Load the image from the file path
                return tk.PhotoImage(file=file_path)
            else:
                # Load the default image data
                return tk.PhotoImage(data=self.default_image_data)

    class Layout:
        #Grid layout dimensions
        maxWidth = 12
        maxHeight = 12

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

    def create_widgets(self):
        #Create colored backgrounds
        # consoleColor = create_colored_frame(self, serialMonitorRow, consoleRowColor)

        #Header
        # headerLabel =  tk.Label(self, text="Sound School", fg=headerFontColor, font=(headerFontStyle, headerFontSize),justify='center', bg=headerRowColor)
        # headerLabel.grid(row=headerRow, column=0, columnspan=maxWidth, sticky="ew", **paddings)

        # Time Display
        self.timeDisplay= tk.Label(self, text=time.strftime("%H:%M:%S", time.localtime()))
        self.timeDisplay.grid(row=self.Layout.timeRow, column=self.Layout.timeColumn, columnspan=self.Layout.timeColumnSpan, **self.Layout.paddings)

        #Port
        self.portSelect = tk.OptionMenu(self, self.selected_port, "No Port Selected")
        self.portSelect.config(width=self.Layout.portWidth)
        self.portSelect.grid(row=self.Layout.portRow, column=self.Layout.portColumn, columnspan=self.Layout.portColumnSpan, sticky="ew", **self.Layout.paddings)

        #Baud
        self.baudSelect = tk.OptionMenu(self, self.selected_baudrate,  *self.baud_options)
        self.selected_baudrate.trace("w", self.disconnect)
        self.baudSelect.config(width=self.Layout.baudWidth)
        self.baudSelect.grid(row=self.Layout.baudRow, column=self.Layout.baudColumn, columnspan=self.Layout.baudColumnSpan,  sticky="ew", **self.Layout.paddings)

        #Address
        self.addressEntry = tk.Entry(self, textvariable=self.selected_address, justify="center", width=self.Layout.addressWidth)
        self.addressEntry.grid(row=self.Layout.addressRow, column=self.Layout.addressColumn, columnspan=self.Layout.addressColumnSpan, sticky="ew", **self.Layout.paddings)

        # Connect
        self.connectButton = tk.Label(self, image=self.Icon.load_image(self, self.Icon.connected), width=self.Layout.connectWidth, height=self.Layout.connectHeight, anchor='center', justify='center', fg=self.Layout.selectorFontColor, font=(self.Layout.selectorFontStyle, self.Layout.selectorFontSize),bg=self.Layout.selectorRowColor)
        self.connectButton.grid(row=self.Layout.connectRow, column = self.Layout.connectColumn, columnspan=self.Layout.connectColumnSpan, sticky="ew", **self.Layout.paddings)
        self.connectButton.bind("<Button-1>", lambda event: self.connect())

        #######################################################

        # Map


        #######################################################

        # Dashboard

        self.dashboard = tk.Frame(self, bg=self.Layout.controlPanelRowColor)
        self.dashboard.grid(row=self.Layout.dashboardRow, column=self.Layout.dashboardColumn, rowspan=self.Layout.dashboardRowSpan, columnspan=self.Layout.dashboardColumnSpan, sticky="ew", **self.Layout.paddings)

        self.dashboard.grid_rowconfigure(0, weight=1)
        self.dashboard.grid_columnconfigure(0, weight=1)


        #######################################################

        # Console
        self.console = tk.Text(self, width=self.Layout.consoleWidth, height=self.Layout.consoleHeight,  padx=15, pady=15)
        self.console.grid(row=self.Layout.consoleRow, column=self.Layout.consoleColumn, rowspan=self.Layout.consoleRowSpan, columnspan=self.Layout.consoleColumnSpan, sticky="ew", **self.Layout.paddings)
        self.console.insert(tk.END, "Console")
        self.console['state'] = 'disabled'

        #######################################################

        # Control Panel

        self.controlPanel = tk.Frame(self, bg=self.Layout.controlPanelRowColor)
        self.controlPanel.grid(row=self.Layout.controlRow, column=self.Layout.controlColumn, rowspan=self.Layout.controlRowSpan, columnspan=self.Layout.controlColumnSpan, sticky="ew", **self.Layout.paddings)

        self.dashboard.grid_rowconfigure(0, weight=1)
        self.dashboard.grid_columnconfigure(0, weight=1)

        #######################################################

        # Other Stuff

        ##savePath = tk.Text(dashboard, width=30, height=1)
        ##savePath.grid(row=savePathRow, column=savePathColumn, rowspan=1, columnspan=savePathColumnSpan, sticky="ew",**paddings)
        ##savePath.insert(tk.END, directory.get())
        ##savePath['state'] = 'disabled'

        #######################################################

        #Set window properties
        self.grid_rowconfigure(self.Layout.maxHeight, weight=1)
        self.grid_columnconfigure(self.Layout.portColumn, weight=1)

    def start(self):
        self.update_pygame()
        self.update_ports()
        self.update_time()
        self.read_serial()

# Execute Tkinter
if __name__ == '__main__':
    # Create instance of UI
    UI = SailUI()
    # Execute Tkinter
    UI.mainloop()
