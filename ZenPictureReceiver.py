#######################################
# 
# Problems to be solved:
# 
# It only actually saves the .txt file when
# the buit .exe is executed as administrator.
# (Perhaps I missed some config during build)
# 
######################################

# For the GUI
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from PIL import ImageTk, Image
Image.LOAD_TRUNCATED_IMAGES = True
ImageTk.LOAD_TRUNCATED_IMAGES = True

# For the Serial
import sys
import glob
import serial

# For the save file option:
from tkinter.filedialog import askdirectory
from datetime import datetime
import shutil
import os

# For the, you guessed it, threads.
from threading import *


class App(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self)

        # Make the app responsive
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=4)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=8)
        self.rowconfigure(3, weight=8)

        # Create value lists for the UI
        self.serial_port_menu_list  = ["", "Select Port"]
        self.baud_rate_menu_list    = ["" ,50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 576000, 921600]
        self.data_bits_menu_list    = ["", 5, 6, 7, 8]
        self.parity_menu_list       = ["", "None", "Even", "Odd", "Mark", "Space"]
        self.stop_bits_menu_list    = ["", "One", "OnePointFive", "Two"]
        self.receive_mode_menu_list = ["", "Line", "Bytes"]
        self.display_mode_menu_list = ["", "Characters", "Bytes"]
        self.message_end_menu_list  = ["", "None", "\\n", "\\r\\n"]

        # Create control variables, also for the UI
        self.default_serial_port_option     = tk.StringVar(value=self.serial_port_menu_list[1])
        self.default_baud_rate_option       = tk.StringVar(value=self.baud_rate_menu_list[17])
        self.default_data_bits_option       = tk.StringVar(value=self.data_bits_menu_list[4])
        self.default_parity_option          = tk.StringVar(value=self.parity_menu_list[1])
        self.default_stop_bits_option       = tk.StringVar(value=self.stop_bits_menu_list[1])
        self.default_receive_mode_option    = tk.StringVar(value=self.receive_mode_menu_list[2])
        self.default_display_mode_option    = tk.StringVar(value=self.display_mode_menu_list[1])
        self.default_message_end_option     = tk.StringVar(value=self.message_end_menu_list[1])
        self.connectedStatus                = tk.BooleanVar(value=False)
        self.firstConnection                = tk.BooleanVar(value=True)

        # Create Serial Control Variables
        self.serial_port_list   = [""];
        self.baud_rate_list     = [50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 576000, 921600]
        self.data_bits_list     = [serial.FIVEBITS, serial.SIXBITS, serial.SEVENBITS, serial.EIGHTBITS]
        self.parity_list        = [serial.PARITY_NONE, serial.PARITY_EVEN, serial.PARITY_ODD, serial.PARITY_MARK, serial.PARITY_SPACE]
        self.stop_bits_list     = [serial.STOPBITS_ONE, serial.STOPBITS_ONE_POINT_FIVE, serial.STOPBITS_TWO]

        # Default values:
        self.selected_serial_port = ""
        self.selected_baud_rate = 115200
        self.selected_data_bits = serial.EIGHTBITS
        self.selected_parity = serial.PARITY_NONE
        self.selected_stop_bits = serial.STOPBITS_ONE
        self.selected_receive_mode = "Bytes"
        self.selected_display_mode = "Characters"
        self.selected_message_end = "None"
        self.currentPictureFolder = "pictures"
        self.setDayDirectory()

        # Serial object:
        self.serialThingy = serial.Serial()

        # Create widgets :)
        self.setup_widgets()



    #### Widget setup ####

    def setup_widgets(self):

        ###  Configuration Menu  ###

        # Create a Frame for the menu
        self.menu_frame = ttk.LabelFrame(self, text="Configuration", padding=(15, 10))
        self.menu_frame.grid(
            row=0, column=0, padx=(20, 10), pady=(20, 10), sticky="nsew"
        )

        # Ports Menu
        self.ports_menu = ttk.OptionMenu(
            #self.menu_frame, self.default_serial_port_option , *self.serial_port_menu_list
            self.menu_frame, tk.StringVar(value="Select Port") , *self.serial_port_list, command=self.optionMenuSelectSerialPort
        )
        self.ports_menu.grid(row=0, column=0, padx=5, pady=2, sticky="nsew")

        # Refresh Button
        self.refresh_button = ttk.Button(self.menu_frame, text="Refresh", command=self.refreshClick)
        self.refresh_button.grid(row=0, column=1, padx=5, pady=2, sticky="nsew")

        # Baud Rate Label
        self.bauds_label = ttk.Label(
            self.menu_frame,
            text="Baud Rate:",
            justify="left",
            font=("-size", 11, "-weight", "normal"),
        )
        self.bauds_label.grid(row=1, column=0, pady=2)

        # Baud Rate Menu
        self.bauds_menu = ttk.OptionMenu(
            self.menu_frame, self.default_baud_rate_option, *self.baud_rate_menu_list, command=self.optionMenuSelectBaudRate
        )
        self.bauds_menu.grid(row=1, column=1, padx=5, pady=2, sticky="nsew")

        # Data Bits Label
        self.data_bits_label = ttk.Label(
            self.menu_frame,
            text="Data Bits:",
            justify="left",
            font=("-size", 11, "-weight", "normal"),
        )
        self.data_bits_label.grid(row=2, column=0, pady=2)

        # Data Bits Menu
        self.data_bits_menu = ttk.OptionMenu(
            self.menu_frame, self.default_data_bits_option, *self.data_bits_menu_list, command=self.optionMenuSelectDataBits
        )
        self.data_bits_menu.grid(row=2, column=1, padx=5, pady=2, sticky="nsew")

        # Parity Label
        self.parity_label = ttk.Label(
            self.menu_frame,
            text="Parity:",
            justify="left",
            font=("-size", 11, "-weight", "normal"),
        )
        self.parity_label.grid(row=3, column=0, pady=2)
        
        # Parity Menu
        self.parity_menu = ttk.OptionMenu(
            self.menu_frame, self.default_parity_option, *self.parity_menu_list, command=self.optionMenuSelectParity
        )
        self.parity_menu.grid(row=3, column=1, padx=5, pady=2, sticky="nsew")
        
        # Stop Bits Label
        self.stop_bits_label = ttk.Label(
            self.menu_frame,
            text="Stop Bits::",
            justify="left",
            font=("-size", 11, "-weight", "normal"),
        )
        self.stop_bits_label.grid(row=4, column=0, pady=2)

        # Stop Bits Menu
        self.stop_bits_menu = ttk.OptionMenu(
            self.menu_frame, self.default_stop_bits_option, *self.stop_bits_menu_list, command=self.optionMenuSelectStopBits
        )
        self.stop_bits_menu.grid(row=4, column=1, padx=5, pady=2, sticky="nsew")

        # Connect Button
        #self.toggle_button = ttk.Checkbutton(
        #    self.menu_frame, text="Connect", style="Toggle.TButton", command=self.connectClick
        #)
        self.connect_button = ttk.Button(self.menu_frame, text="Connect", command=self.connectClick)
        self.connect_button.grid(row=5, column=0, columnspan=2 ,padx=5, pady=2, sticky="nsew")

        self.menu_frame.columnconfigure(0, weight=3)
        self.menu_frame.columnconfigure(1, weight=1)
        self.menu_frame.rowconfigure(0, weight=1)
        self.menu_frame.rowconfigure(1, weight=1)
        self.menu_frame.rowconfigure(2, weight=1)
        self.menu_frame.rowconfigure(3, weight=1)
        self.menu_frame.rowconfigure(4, weight=1)
        self.menu_frame.rowconfigure(5, weight=1)


        ###  Control Pannel  ###
        
        # Create a Frame for the Control Pannel
        self.control_pannel_frame = ttk.LabelFrame(self, text="Controls", padding=(15, 10))
        self.control_pannel_frame.grid(
            row=1, column=0, padx=(20, 10), pady=(5, 10), sticky="nsew"
        )

        # Saving To Label
        self.saving_to_label = ttk.Label(
            self.control_pannel_frame,
            text="Saving to:",
            justify="left",
            anchor="w",
            font=("-size", 11, "-weight", "normal"),
        )
        self.saving_to_label.grid(row=0, column=0, pady=2, sticky = "w")

        # Directory Label
        self.directory_label = ttk.Label(
            self.control_pannel_frame,
            text=f'{self.currentPictureFolder}/{self.currentDirName}',
            justify="left",
            anchor="w",
            font=("-size", 11, "-weight", "normal"),
        )
        self.directory_label.grid(row=1, column=0, pady=2, sticky = "w")

        # Change Dir Button
        self.save_to_file_button = ttk.Button(self.control_pannel_frame, text="Change folder", command=self.setCurrentPictureFolder)
        self.save_to_file_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        self.control_pannel_frame.columnconfigure(0, weight=1)
        self.control_pannel_frame.rowconfigure(0, weight=1)
        self.control_pannel_frame.rowconfigure(1, weight=1)
        self.control_pannel_frame.rowconfigure(2, weight=1)

        # ###  Rolling Text Terminal  ###

        # # Create a Frame for the terminal
        # self.terminal_frame = ttk.LabelFrame(self, text="Terminal", padding=(20, 10))
        # self.terminal_frame.grid(
        #     row=0, column=1, columnspan=1, rowspan=4, padx=(10, 10), pady=(20, 5), sticky="nsew"
        # )

        # self.main_terminal = scrolledtext.ScrolledText(self.terminal_frame, wrap = tk.WORD, font =("Calibri", 12), bg="#333333", borderwidth=0)
        # self.main_terminal.grid(row=0, rowspan=4, column=0, pady=(2,10), sticky="nsew")
        # self.main_terminal.tag_config('RX', foreground='#CCCCCC')
        # self.main_terminal.tag_config('TX', foreground='#66B3FF')

        # self.terminal_frame.columnconfigure(0, weight=1)
        # self.terminal_frame.rowconfigure(0, weight=1)
        # self.terminal_frame.rowconfigure(1, weight=1)
        # self.terminal_frame.rowconfigure(2, weight=1)
        # self.terminal_frame.rowconfigure(3, weight=1)

        ### Image display ###

        # Create a Frame for the image
        self.image_frame = ttk.LabelFrame(self, text="Received picture", padding=(20, 10))
        self.image_frame.grid(
             row=0, column=1, columnspan=5, rowspan=4, padx=(10, 10), pady=(20, 5), sticky="nsew"
        )

        # Used later for resizing image in zooming in and out
        self.image_frame_width = None
        self.image_frame_height = None

        self.original_image = Image.open("StandardPicture.png")
        self.current_image = self.original_image
        self.current_photo_image = ImageTk.PhotoImage(self.current_image)

        # Label soon to be an image
        self.image_label = ttk.Label(
            self.image_frame,
            image = self.current_photo_image,
            anchor="center",
        )
        self.image_label.grid(row=0, rowspan=4, column=0, columnspan=5, pady=(10, 10), sticky="nsew")

        # Zoom In Button
        self.zoom_in_button = ttk.Button(self.image_frame, text="+", command=self.zoomIn)
        self.zoom_in_button.grid(row=4, column=3, pady=(10, 10), sticky="nsew")

        self.zoom_ammount = tk.DoubleVar(value=100)
        # Zoom Value Label
        self.zoom_values_label = ttk.Label(
            self.image_frame,
            text="100%",
            anchor="center",
            font=("-size", 11, "-weight", "normal"),
        )
        self.zoom_values_label.grid(row=4, column=2, pady=(10, 10), sticky="nsew")

        # Zoom Out Button
        self.zoom_out_button = ttk.Button(self.image_frame, text="-", command=self.zoomOut)
        self.zoom_out_button.grid(row=4, column=1, pady=(10, 10), sticky="nsew")

        
        # self.zoom_scale = ttk.Scale(
        #     self.image_frame,
        #     from_=50,
        #     to=150,
        #     variable=self.zoom_ammount,
        #     command=self.zoomUpdate,
        #     #command=lambda event: self.zoom_ammount.set(self.zoom_scale.get()),
        # )
        # self.zoom_scale.grid(row=4, column=2, padx=(10, 10), sticky="nsew")

        self.image_frame.columnconfigure(0, weight=5)
        self.image_frame.columnconfigure(1, weight=1)
        self.image_frame.columnconfigure(2, weight=1)
        self.image_frame.columnconfigure(3, weight=1)
        self.image_frame.columnconfigure(4, weight=5)

        self.image_frame.rowconfigure(0, weight=1)
        self.image_frame.rowconfigure(1, weight=1)
        self.image_frame.rowconfigure(2, weight=1)
        self.image_frame.rowconfigure(3, weight=1)


        ###  Message Entry  ###
        
        # Frame for the message entry and button
        self.entry_frame = ttk.LabelFrame(self,text="Send Data", padding=(0, 0, 0, 10))
        self.entry_frame.grid(
            row=4, column=1, padx=10, pady=(5, 5), sticky="nsew", rowspan=3
        )
        self.entry_frame.columnconfigure(index=0, weight=1)

        # Message Entry
        self.message_entry = ttk.Entry(self.entry_frame)
        #self.message_entry.insert(0, "Send Data")
        self.message_entry.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        # Message Send Button
        self.send_button = ttk.Button(self.entry_frame, text="Send", command = self.sendMessage)
        self.send_button.grid(row=0, column=1 ,padx=10, pady=5, sticky="nsew")

        self.entry_frame.columnconfigure(0, weight=8)
        self.entry_frame.columnconfigure(1, weight=1)
        self.entry_frame.rowconfigure(0, weight=1)

        # Sizegrip
        self.sizegrip = ttk.Sizegrip(self)
        self.sizegrip.grid(row=100, column=100, padx=(0, 5), pady=(0, 5))


    #### Buttons functions ####
    def clearTerminalClick(self):
        self.main_terminal.delete('1.0', tk.END)

    def sendMessage(self):
        Thread(target=SerialWrite, args=(self, self.message_entry.get(),)).start()

    def refreshClick(self):
        """ Lists serial port names on Windows, Linux or Mac.
    
            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(50)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')
    
        result = [""]
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass

        print("result:")       
        print(result)

        # redo this later using (https://stackoverflow.com/questions/19794069/tkinter-gui-update-choices-of-an-option-menu-depending-on-a-choice-from-another)

        if(len(result) != 1):
            self.serial_port_list = result
            self.selected_serial_port = self.serial_port_list[1]

            self.ports_menu = ttk.OptionMenu(
                self.menu_frame, tk.StringVar(value=self.serial_port_list[1]), *self.serial_port_list, command=self.optionMenuSelectSerialPort
            )
            self.ports_menu.grid(row=0, column=0, padx=5, pady=2, sticky="nsew")
        
        else:
            self.ports_menu = ttk.OptionMenu(
                self.menu_frame, tk.StringVar(value="No ports found"), *[""]
            )
            self.ports_menu.grid(row=0, column=0, padx=5, pady=2, sticky="nsew")

    def connectClick(self):
        if (self.connectedStatus.get() == False and self.selected_serial_port != ""):
            SerialConnect(self)

            if(self.firstConnection.get() == True):
                # Start background thread
                Thread(target=SerialTerminal, args=(app,)).start()
                self.firstConnection.set(False)

        else:
            SerialDisconnect(self)

    def updateConnectButton(self):
        if(self.connectedStatus.get() == True):
            self.connect_button.config(text="Disconnect", style="Accent.TButton")
            self.send_button.config(style="Accent.TButton")
        else:
            self.connect_button.config(text="Connect", style="")
            self.send_button.config( style="")


    #### Zoom functions ####
    def zoomIn(self):
        print("Zoom in")

        # Limit the zoom ammount:
        if(self.zoom_ammount.get() < 200):
            self.zoom_ammount.set(self.zoom_ammount.get() + 10)
            print(self.zoom_ammount.get()/100)

            self.updateImage(self.original_image) # It accesses the zoom_ammount as a global variable

            self.zoom_values_label.configure(text = f'{round(self.zoom_ammount.get())}%')
        
        
    def zoomOut(self):
        print("Zoom out")
        if(self.zoom_ammount.get() > 50):
            self.zoom_ammount.set(self.zoom_ammount.get() - 10)
            print(self.zoom_ammount.get()/100)
            
            self.updateImage(self.original_image)

            self.zoom_values_label.configure(text = f'{round(self.zoom_ammount.get())}%')

    def updateImage(self, picture):
        self.original_image = picture
        self.current_image = self.original_image
        self.current_image = self.current_image.resize((round((self.zoom_ammount.get()/100)*self.current_image.width), round((self.zoom_ammount.get()/100)*self.current_image.height)))
        self.current_photo_image = ImageTk.PhotoImage(self.current_image)
        self.image_label.configure(image = self.current_photo_image)

    #### File management functions ####
    def updateFileName(self, fileName):
        self.image_frame.configure(text = f'Received picture - {fileName}')

    def setDayDirectory(self):
        self.currentDirName = datetime.now().strftime("%Y-%m-%d")
        if not os.path.exists(self.currentPictureFolder + '/' + self.currentDirName):
            os.makedirs(self.currentPictureFolder + '/' + self.currentDirName)
            self.updateDirLabel()
    
    def setCurrentPictureFolder(self):
        newDirectory = askdirectory()

        if(newDirectory != ""): # The operation wasn't canceled by the user
            self.currentPictureFolder = newDirectory
            self.updateDirLabel()
        else:
            pass

    def updateDirLabel(self):
        self.directory_label.configure(text = f'{self.currentPictureFolder}/{self.currentDirName}')


    def optionMenuSelectSerialPort(self, value):
        self.selected_serial_port = value
        self.serialThingy.port = self.selected_serial_port

    def optionMenuSelectBaudRate(self, value):
        self.selected_baud_rate = self.baud_rate_list[self.baud_rate_menu_list.index(value) - 1]
        self.serialThingy.baudrate = self.selected_baud_rate

    def optionMenuSelectDataBits(self, value):
        self.selected_data_bits = self.data_bits_list[self.data_bits_menu_list.index(value) - 1]
        self.serialThingy.bytesize = self.selected_data_bits

    def optionMenuSelectParity(self, value):
        self.selected_parity = self.parity_list[self.parity_menu_list.index(value) - 1]
        self.serialThingy.parity = self.selected_parity

    def optionMenuSelectStopBits(self, value):
        self.selected_stop_bits = self.stop_bits_list[self.stop_bits_menu_list.index(value) - 1]
        self.serialThingy.stopbits = self.selected_stop_bits

    def optionMenuSelectReceiveMode(self, value):
        self.selected_receive_mode = value

    def optionMenuSelectDisplayMode(self, value):
        self.selected_display_mode = value

    def optionMenuSelectMessageEnd(self, value):
        self.selected_message_end = value


#   def ReceiveModeHelper_enter(self, event):
#       self.receive_mode_label.configure(
#           text="Lines: waits for a '\\n' (faster)\nBytes: displays bytes\ninstantly (slower)",
#           justify="left",
#           font=("-size", 8, "-weight", "normal"))

#   def ReceiveModeHelper_leave(self, enter):
#       self.receive_mode_label.configure(
#           text="Receive Mode:",
#           justify="left",
#           font=("-size", 11, "-weight", "normal"))


def SerialConnect(app):
    app.serialThingy.port = app.selected_serial_port
    app.serialThingy.baudrate = app.selected_baud_rate
    app.serialThingy.parity = app.selected_parity
    app.serialThingy.stopbits = app.selected_stop_bits
    app.serialThingy.bytesize = app.selected_data_bits

    try:
        app.serialThingy.open()
    except:
        print("Something went wrong when oppening the serial port")

    if(app.serialThingy.is_open):
        app.connectedStatus.set(True)
        app.updateConnectButton()        


def SerialDisconnect(app):
    app.serialThingy.close()

    if(not app.serialThingy.is_open):
        app.connectedStatus.set(False)
        app.updateConnectButton()
    else:
        print("Something went wrong when closing the serial port")


def SerialTerminal(app):

    searchCounter = 0
    byteCounter = 0
    deadBeefFound = False

    while True: # Main thread loop

        bufferFile = open("temp.jpg", "wb")

        print("\nWaiting for serial data to arrive.\n")

        while True: # This one will end in some instances, than will be restarted
            if(app.connectedStatus.get() == True and app.serialThingy.is_open):
                try:
                    char = app.serialThingy.read()
                    byte = ord(char)
                    # print(f'data: {byte}')
                    # print("{out:02X} ".format(out = ord(byte)) + ' ')
                    if(searchCounter == 0 and byte == 0xDE):
                        searchCounter += 1
                    elif (searchCounter == 1 and byte == 0xAD):
                        searchCounter += 1
                    elif (searchCounter == 2 and byte == 0xBE):
                        searchCounter += 1
                    elif (searchCounter == 3 and byte == 0xEF):
                        if(deadBeefFound == True):
                            deadBeefFound = False
                            searchCounter = 0
                            break
                        
                        searchCounter = 4
                    elif (searchCounter == 4):
                        deadBeefFound = True
                        searchCounter = 0
                    else:
                        searchCounter = 0
    
                    if(deadBeefFound):
                        #print("{out:02X} ".format(out = ord(char)) + ' ') # Jesus fucking christ python, learn with C: printf("%.2X ",byte)
                        #print(".")
                        bufferFile.write(byte.to_bytes(1, 'big'))
                        byteCounter += 1
    
                except:
                    print("Error reading from port. Perhaps it has been disconnected.")
                    SerialDisconnect(app)

        bufferFile.close()

        print("\nCopying contents:")
        outputFileName = datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss.jpg")
        print(f'outputFileName: {outputFileName}')

        # Check for day folder - Basically added for 23:59 -> 00:00 transitions
        app.setDayDirectory() # Updates app.currentDirName
        outputFileAddr = app.currentPictureFolder + '/' + app.currentDirName + '/' + outputFileName

        # Create a new output file:
        outputFile = open(outputFileAddr, "wb")
        outputFile.close()

        # The final three bytes are going to be 0xDE 0xAD 0xBE
        shutil.copyfile('temp.jpg',outputFileAddr)
        os.remove("temp.jpg")

        # Removing last three bytes:
        outputFile = open(outputFileAddr, "rb+")
        outputFile.seek(-3, 2)
        outputFile.truncate()
        outputFile.close()

        try:
            # Try to open that image and load the data
            Image.open(outputFileAddr).load()
            app.updateFileName(outputFileName)
            app.updateImage(Image.open(outputFileAddr))
        except OSError:
            # ImageTk does not like truncated images
            print("Half baked image detected. It was saved in the files but will no be shown.")

        
def SerialWrite(app, data):
    if(app.connectedStatus.get() and len(data) > 0):

        terminalText = "\n>> " + data + '\n'

        if(app.selected_message_end == "\\n"):
            data += '\n'
        elif(app.selected_message_end == "\\r\\n"):
            data += '\r\n'
        
        app.serialThingy.write(str.encode(data))
        app.main_terminal.insert(tk.END, terminalText, 'TX')
        app.main_terminal.see("end")


def on_close():
    root.destroy()


if __name__ == "__main__":

    # Prepare the photos directory beforehand:
    if not os.path.exists("pictures"):
        os.makedirs("pictures")

    # Start with the Tk app:
    root = tk.Tk()
    root.title("Zenith Picture Receiver")
    icon = Image.open('ZenPictureReceiverIcon.bmp')
    photo = ImageTk.PhotoImage(icon)
    root.wm_iconphoto(True, photo)

    # Set the theme
    root.tk.call("source", "azure.tcl")
    root.tk.call("set_theme", "dark")

    global app
    app = App(root)
    app.pack(fill="both", expand=True)
    app.setDayDirectory()

    # Set a minsize for the window, and place it in the middle
    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    x_cordinate = int((root.winfo_screenwidth() / 2) - (root.winfo_width() / 2))
    y_cordinate = int((root.winfo_screenheight() / 2) - (root.winfo_height() / 2))
    root.geometry("+{}+{}".format(x_cordinate, y_cordinate-20))

    root.protocol("WM_DELETE_WINDOW",  on_close)
    root.mainloop()


    # For data handling do this:
    # https://stackoverflow.com/questions/45383771/equivalent-c-union-in-python
    
    # Add date and time to jpeg metadata with this:
    # https://stackoverflow.com/questions/58780073/how-do-i-add-date-time-properties-to-my-jpg-files-using-python-for-correct-inde
    
    # In te future, save temporary files and ask to save on closing when there is no directory set:
    # https://stackoverflow.com/questions/111155/how-do-i-handle-the-window-close-event-in-tkinter

    # Copy image right click menu:
    # https://www.geeksforgeeks.org/right-click-menu-using-tkinter/




    ## TRASH CAN ##

            # self.image_frame_width = 0.9 * self.image_frame.winfo_width()
            # self.image_frame_height = 0.9 * self.image_frame.winfo_height()
    
            # print('Frame Width:')
            # print(self.image_frame_width)
    
            # print('Frame Height:')
            # print(self.image_frame_height)
    
            # print('Image Width:')
            # print(self.current_image.width)
    
            # print('Image Height:')
            # print(self.current_image.height)
    
            # if(self.image_frame_width > self.image_frame_height):
            #      self.resize_ratio = self.image_frame_height/self.current_image.height
            # else:
            #      self.resize_ratio = self.image_frame_width/self.current_image.width
    
            # print('Ratio:')
            # print(self.resize_ratio)