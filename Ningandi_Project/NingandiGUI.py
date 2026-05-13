#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import threading
import time
import sys
import signal


#Adaptative paths for the project based on the current execution path
project_path = os.path.dirname(os.path.abspath(__file__))
ascii_path = os.path.join(project_path, "project_images", "ASCIIIMG.txt")
icon_path = os.path.join(project_path, "project_images", "Ningandi2.png")
server_path = os.path.join(project_path, "Ningandi.py")
#Colors for text printed in terminal
RED    =     "\x1b[31m"
GREEN  =     "\x1b[32m"
YELLOW =     "\x1b[33m"
RESET  =     "\x1b[0m"
#Define a color scheme (I'll tweak these hex values later for perfect hue)
BG_COLOR = "#2b2b2b"          #dark background
BUTTON_COLOR = "#00a1b6"      #dark cyan 
BUTTON_HOVER = "#00bcd4"      #lighter cyan on hover
TEXT_COLOR = "#ffffff"        #White text
ACCENT_COLOR = "#4CAF50"      #Use for status indicator text
NINGRED_COLOR = "#e53935"     #bright red
#Define fonts I'll reuse
TITLE_FONT = ("Segoe UI", 16, "bold")
BUTTON_FONT = ("Segoe UI", 11, "bold")
#Store the server process globally
server_process = None 
subprocess.run(["sudo", "-v"], check=True) 
#Hotspot interface function we check the file with the interface that was generated during installation to use it as a referenece
def load_hotspot_interface():
    interface_path=os.path.join(project_path, "interface.txt")
    try:
        with open(interface_path, "r") as f:
            interface = f.read().strip()
            if interface:
                print(f"{GREEN}Loaded hotspot interface: {interface}{RESET}") 
                return interface
            
    except FileNotFoundError:
        print(f"{RED}interface.txt not found at {interface_path}{RESET}")
            
    except Exception as e:
        print(f"{RED}Error reading interface.txt: {e}{RESET}")
        return None
#Turn my old gradient loop stratergy into a function so I don't have to set it manually for each new top level window I make
def apply_dark_gradient(canvas, start_color_value=39, range_value=30):
  
    #Get canvas dimensions
    canvas.update_idletasks()      #Ensure dimensions are updated 
    width = canvas.winfo_width()   #Get width
    height = canvas.winfo_height() #Get height
    
    #Create gradient lines
    for i in range(height):                                        #Loop from pixel 0 to the max height
        ratio = i / height if height > 0 else 0                    #Convert current position into decimal between 0 and 1
        color_val = int(start_color_value + (range_value * ratio)) #Color_val = starting color decimal value  plus (30 range times ratio int value)
        color_val = max(0, min(255, color_val))                    #Clamp color_val between 0 and 255
        color = f'#{color_val:02x}{color_val:02x}{color_val:02x}'  # :02x converts to hexadecimal values of 2 digits padded with zeros if needed.
        canvas.create_line(0, i, width, i, fill=color, width=1)    #Creates a line from x to y.  From possition x=0, y=i to position x=max width, y=i, fill is the color and width is the number of pixels thickness drawn per loop count (1 pixel high)


#Detect which DNS solution is available on the system
def detect_dns_solution():
    global detected_dns_solution
    
    solutions_to_check = [
        "systemd-resolved", 
        "unbound", 
        "named",
        "knotd",
        "pdns_recursor"]
    
    active_solution = None      #Stores the first one that returns 0
    inactive_solution = None    #Stores the first one that returns 3
    
    for solution in solutions_to_check:
        result = subprocess.run(
            ["systemctl", "is-active", solution],
            capture_output=True)
        
        if result.returncode == 0:  #Service is running
            active_solution = solution
            break  #Found active one, stop searching
        elif result.returncode == 3 and inactive_solution is None:  #Service exists but stopped
            inactive_solution = solution  #Store first one that exists
    
    #Prioritize: active first, then inactive
    if active_solution:
        detected_dns_solution = active_solution
        print(f"{GREEN}Detected DNS solution: {detected_dns_solution} (active){RESET}")
        return active_solution
    elif inactive_solution:
        detected_dns_solution = inactive_solution
        print(f"{YELLOW}Detected DNS solution: {detected_dns_solution} (inactive){RESET}")
        return inactive_solution
    else:
        #No DNS solution found
        detected_dns_solution = None
        print(f"{YELLOW}No DNS solution detected{RESET}")
        return None

def get_dns_commands(action):
    #Generate the correct commands based on detected DNS solution
    global detected_dns_solution
    
    if not detected_dns_solution:
        return None
    
    #Return commands as a list for the functions
    return ["sudo", "systemctl", action, detected_dns_solution]

def show_error_dialog(parent, error_msg):
    #Show error dialog and exit
    dialog = CustomMessageBox(parent, "Error", error_msg, msg_type="info")
    parent.wait_window(dialog)
    sys.exit(1)


#custom mesage box functions using top level windows
class CustomMessageBox(tk.Toplevel):
    def __init__(self, parent, title, message, msg_type="info"):
        super().__init__(parent)
        self.title(title)
        self.geometry("350x180")
        self.resizable(False, False)
        canvas = tk.Canvas(
        self,
        width=400,
        height=180, 
        highlightthickness=0, 
        bg=BG_COLOR)
        canvas.place(
        x=0, 
        y=0, 
        relwidth=1, 
        relheight=1) 
        self.configure(bg=BG_COLOR)
        self.result = None
        self.msg_type = msg_type
        #Make it modal (blocks interaction with parent window)
        self.transient(parent)
        self.grab_set()
        apply_dark_gradient(canvas)
        #Messages settings
        canvas.create_text(180, 40, 
            text=message,  
            font=("Segoe UI", 12, "bold"), 
            fill=TEXT_COLOR,
            width=370)
        
        #Create buttons based on type
        if msg_type == "warning":
            tk.Button(self,
                text="OK", 
                bg=BUTTON_COLOR, 
                fg=TEXT_COLOR, 
                font=BUTTON_FONT, 
                padx=30, 
                pady=8, 
                cursor="hand2",
                highlightthickness=0,
                activebackground=BUTTON_HOVER, 
                activeforeground=TEXT_COLOR,
                relief=tk.FLAT,
                overrelief=tk.RAISED,
                bd=1.5,
                command=lambda: self.done(True)).place(x=70, y=100) #With .place I can set the exact coordinates for each button
            tk.Button(self, 
                text="Cancel", 
                bg="#c62828", 
                fg=TEXT_COLOR, 
                font=BUTTON_FONT, 
                padx=14, 
                pady=8, 
                cursor="hand2",
                highlightthickness=0,
                activebackground=NINGRED_COLOR, 
                activeforeground=TEXT_COLOR,
                relief=tk.FLAT,
                overrelief=tk.RAISED,
                bd=1.5,
                command=lambda: self.done(False)).place(x=200, y=100)
        else: 
            tk.Button(
                self, 
                text="OK", 
                bg=BUTTON_COLOR, 
                fg=TEXT_COLOR, 
                font=BUTTON_FONT, 
                padx=30, 
                pady=8, 
                cursor="hand2",
                highlightthickness=0,
                activebackground=BUTTON_HOVER, 
                activeforeground=TEXT_COLOR,
                relief=tk.FLAT,
                overrelief=tk.RAISED,
                bd=1.5,
                command=lambda: self.done(True)).place(relx=0.5, rely=0.7, anchor="center")  #Anchor the button to relative position
        
        #Center the window on parent
        self.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        x = parent_x + (parent_width - 350) // 2
        y = parent_y + (parent_height - 180) // 2
        self.geometry(f"+{x}+{y}")
    
    def done(self, result):
        self.result = result
        self.destroy()

def custom_showwarning(parent, title, message):
    
    dialog = CustomMessageBox(parent, title, message, msg_type="warning")
    parent.wait_window(dialog)
    return dialog.result if dialog.result is not None else False

def custom_showinfo(parent, title, message):
    
    dialog = CustomMessageBox(parent, title, message, msg_type="info")
    parent.wait_window(dialog)
    return dialog.result



def start_server():
    global server_process
    #Check if server is already running (this one is mandatory)
    if server_process is not None and server_process.poll() is None:
        custom_showinfo(root, "‼ Error", "⃠  Server is already running!")
        return
    #Warning mesage since dnsmasq gives error while hotspot is on
    result = custom_showwarning(root, "⚠Warning⚠", "Turn OFF your hotspot before continuing!")
    
    if result:
        if detected_dns_solution is not None:
            #Stop the current DNS solution
            subprocess.run(get_dns_commands("stop"), capture_output=True)
            subprocess.run(get_dns_commands("disable"), capture_output=True)
        #Enable and start dnsmasq
        subprocess.run(["sudo", "cp", "~/dnsmasq.conf-edited", "/etc/dnsmasq.conf"], capture_output=True)
        subprocess.run(["sudo", "systemctl", "enable", "dnsmasq"], capture_output=True)
        subprocess.run(["sudo", "systemctl", "start", "dnsmasq"], capture_output=True)
        #Start the server
        server_process = subprocess.Popen(["sudo", "python3", server_path])
        
        
        #Print art if can otherwise print error and move on with the code
        print("\n")
        try:
            with open(ascii_path, 'r') as asciifile:
                content = asciifile.read()
                print(content)
        except FileNotFoundError:
            print(f"Error: file '{ascii_path}' not found")
        except Exception as err:
            print(f"Error: {err}")


        custom_showinfo(root, "Ready", "✅Your server is ready!\nStart your hotspot now!") #If users complain about segfaults remove all the unicode emojis 

def stop_server():
    global server_process
    
    #Check if server is not running or was stopped
    if server_process is None or server_process.poll() is not None:
        custom_showinfo(root, "‼  Error", "⃠  Server is not running!")
        return
    #Create custom window so it closes automatically
    stopping_window = tk.Toplevel(root)
    stopping_window.title("⚠Stopping⚠")
    stopping_window.geometry("300x100")
    stopping_window.configure(bg=BG_COLOR)
    canvas = tk.Canvas(
    stopping_window,
    width=400, 
    height=250, 
    highlightthickness=0,
    bg=BG_COLOR)
    canvas.place(
    x=0, 
    y=0, 
    relwidth=1,  
    relheight=1)
    apply_dark_gradient(canvas)
    #Center relative to main window, update idletask to get dimentions
    stopping_window.update_idletasks()
    main_x = root.winfo_x()
    main_y = root.winfo_y()
    main_width = root.winfo_width()
    main_height = root.winfo_height()
    window_width = stopping_window.winfo_width()
    window_height = stopping_window.winfo_height()
    #Simple arithmetic equation to center it
    x = main_x + (main_width - window_width) // 2
    y = main_y + (main_height - window_height) // 2
    stopping_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    #The window text itself
    canvas.create_text(150, 40, 
        text="⚠stopping server,\nplease wait...⚠",  
        font=("Segoe UI", 12, "bold"), 
        fill="#ffeb3b",
        width=370)

    #Run stopping in background thread so dialog "auto closes"
    def stop_background():
        #Record start time of this function
        start_time = time.time() 
        if server_process:  
            if server_process.poll() is None: #none means process is still running
                #SIGTERM is the command to stop server nicely no force 
                subprocess.run(["sudo", "kill", "-SIGTERM", str(server_process.pid)], capture_output=True)
                #Wait for it to finish
                server_process.wait()
        
        #Commands to restore normal DNS functionality by stopping dnsmasq and starting the default DNS solver if any
        
        #Stop dnsmasq
        subprocess.run(["sudo", "systemctl", "stop", "dnsmasq"], capture_output=True)
        subprocess.run(["sudo", "systemctl", "disable", "dnsmasq"], capture_output=True)
        subprocess.run(["sudo", "cp", "~/dnsmasq.conf-clean", "/etc/dnsmasq.conf"], capture_output=True) #This file swappings is for users with dnsmasq as default DNS solution in case you were wondering doesn't affect normal users in any way
        
        if detected_dns_solution is not None:
            #Restart the detected DNS solution
            subprocess.run(get_dns_commands("enable"), capture_output=True)
            subprocess.run(get_dns_commands("start"), capture_output=True)
        print(f"{RED}Server stopped{RESET}")
        
        #Make sure window is up for at least one second if the server stops faster than in 1 second otherwise the mesage will stay as long as the server takes to stop
        elapsed = time.time() - start_time
        if elapsed < 1:
            time.sleep(1 - elapsed) 
        #Now close the stopping window automatically 
        def finish_stopping():
            stopping_window.destroy()
            custom_showinfo(root, "Done✅", "✅ Server stopped, DNS restored!")
        root.after(0, finish_stopping)

    thread = threading.Thread(target=stop_background)
    thread.daemon = True 
    thread.start()

#Closing function just in case user closes gui while server is running
def on_closing():
    global server_process
    if server_process:
        if server_process.poll() is None:
            #If the server is running then kill it
            subprocess.run(["sudo", "kill", "-SIGTERM", str(server_process.pid)], capture_output=True)
            server_process.wait()  
    #Restore DNS function disabling dnsmasq and restoring detected DNS solution if any
    subprocess.run(["sudo", "systemctl", "stop", "dnsmasq"], capture_output=True)
    subprocess.run(["sudo", "systemctl", "disable", "dnsmasq"], capture_output=True)
    subprocess.run(["sudo", "cp", "~/dnsmasq.conf-clean", "/etc/dnsmasq.conf"], capture_output=True)
    if detected_dns_solution is not None:
        subprocess.run(get_dns_commands("enable"), capture_output=True)
        subprocess.run(get_dns_commands("start"), capture_output=True)
    #Reset WiFi if server was done running this step is crucial to clean up dnsmasq user may miss or ignore a mesage box so I do it for them
    if server_process and server_process.poll() is not None: 
        print(f"{YELLOW}Resetting wifi...{RESET}")
        
        try:
            #Try rfkill first
               
            subprocess.run(["sudo", "rfkill", "block", "wifi"], capture_output=True, check=True)
            time.sleep(1) #Brief pause in between 
            subprocess.run(["sudo", "rfkill", "unblock", "wifi"], capture_output=True, check=True)
            print(f"{GREEN}WiFi reset successful{RESET}")
        except subprocess.CalledProcessError as e:
            print(f"return code: {e.returncode}")
            print(f"rfkill failed - stdout: {e.stdout}")
            print(f"rfkill failed - stderr: {e.stderr}")
            #Fall back to ip link
            if HOTSPOT_INTERFACE:
                try:
                    subprocess.run(["sudo", "ip", "link", "set", HOTSPOT_INTERFACE, "down"], capture_output=True, check=True)
                    time.sleep(1)
                    subprocess.run(["sudo", "ip", "link", "set", HOTSPOT_INTERFACE, "up"], capture_output=True, check=True)
                    print(f"{GREEN}WiFi reset successful{RESET}")
                except subprocess.CalledProcessError as e:
                    print(f"{RED}WiFi reset failed: {e}{RESET}")
    else:
        print(f"{YELLOW}No hotspot interface configured, skipping WiFi reset{RESET}") #At this point if it didn't work I tried the user must do it manually
    
    print(f"{YELLOW}GUI closed, DNS cleanup, exiting...{RESET}")
    
    root.destroy()

#Signal managing in case users close the user use crtl + C on the terminal to close the program and stop server
def signal_handler(signum, frame):
    #Handle termination signals gracefully
    print(f"\n{YELLOW}Signal received, shutting down...{RESET}")
    on_closing()

#Register signal handlers for using Ctrl+C or closing terminal window.
signal.signal(signal.SIGINT, signal_handler)   
signal.signal(signal.SIGTERM, signal_handler)  #Terminal close/kill signal, closing the terminal doesn't trigger my on_closing funtion on all distros due to the way different distros handles closing terminal windows

#Run DNS solution detection at startup
detect_dns_solution()
HOTSPOT_INTERFACE = load_hotspot_interface()
#Create the main window
root = tk.Tk()
canvas = tk.Canvas(
root,
width=400, #Not used since I bound the canvas to window size  
height=250, #Same as above ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
highlightthickness=0, #0 to disable it color setting on it doesn't work on my machine 
bg=BG_COLOR)
canvas.place(
x=0, 
y=0, 
relwidth=1,  #Bind width to window size
relheight=1) #Bind height to window size



root.title("Ningandi Controller")
#add icon, check if the file is there if not give error and move on
if os.path.exists(icon_path):
    try:
        icon = tk.PhotoImage(file=icon_path)
        root.iconphoto(True, icon) #True makes any other window oppened by tkinter have the same icon. False only this one.
    except tk.TclError: #Specific error that tkinter uses in case the file isn't readable for some reason
        print(f"Error: Could not load icon from {icon_path}")
else:
    print(f"Error: Icon not found at {icon_path}") #May seem redundant but it isn't this is if the file isn't there at all

root.geometry("350x250")
root.resizable(False, False)  #no resize of main window x, y
root.configure(bg=BG_COLOR)

apply_dark_gradient(canvas)
#tell window what to do when user clicks the X close button
root.protocol("WM_DELETE_WINDOW", on_closing)


#Title label at the top with spacing
title_label = tk.Label(root,
    text="Ningandi",
    font=("dyuthi", 22, "bold"),  #I really liked this font for the title
    bg=BG_COLOR,
    fg="#ffffff")
title_label.pack(pady=(30, 10))  #Top and bottom padding


#Create the buttons
start_button = tk.Button(
    root,
    text="▶ Start Server",
    command=start_server,
    font=BUTTON_FONT,
    bg=BUTTON_COLOR,
    fg=TEXT_COLOR,
    activebackground=BUTTON_HOVER,
    activeforeground=TEXT_COLOR,
    relief=tk.FLAT,
    overrelief=tk.RAISED,
    bd=1.5,
    highlightthickness=0, #Didnt like the highligt it didn't change color in my machine, = 0 to remove the border completely
    padx=30,
    pady=12,
    cursor="hand2")
start_button.pack(pady=10)
#Now the stop button
stop_button = tk.Button(
    root,
    text="■ Stop Server",
    command=stop_server,
    font=BUTTON_FONT,
    bg="#c62828", 
    fg=TEXT_COLOR,
    activebackground=NINGRED_COLOR,
    activeforeground=TEXT_COLOR,
    relief=tk.FLAT,
    overrelief=tk.RAISED,
    bd=1.5,
    highlightthickness=0,  #If this can change color in your machine just increase from 0 and add: highlightcolor=<hex values>  it's too ugly anyway
    padx=30,
    pady=12,
    cursor="hand2")
stop_button.pack(pady=10)
#Now the staus indicator that dinamically changes based on server status
status_text = canvas.create_text(180, 230, # pos X, Y
    text="Server Status: OFF",
    font=("uroob", 12, "bold"),
    fill=NINGRED_COLOR) #Fill in canvas is text color

#Function to check status and update the status in real time
def update_server_status():
    global server_process
    if server_process is None:
        canvas.itemconfig(status_text, 
        text="Server Status: OFF", 
        fill=NINGRED_COLOR)
    elif server_process.poll() is None:
        #poll() returns None when the process is still running
        canvas.itemconfig(status_text, 
        text="Server Status: ON", 
        fill=ACCENT_COLOR)
    else:
        #poll() returns exit code if  process was terminated so just in case
        canvas.itemconfig(status_text, 
        text="Server Status: OFF", 
        fill=NINGRED_COLOR)
    #Check every 3 seconds (3000 miliseconds)
    root.after(3000, update_server_status)

#Start the status check as soon as the app starts
update_server_status()

#run the app
root.mainloop()
