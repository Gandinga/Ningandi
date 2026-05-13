#!/bin/bash

#Variables to reuse
PROJECT_FOLDER="./Ningandi_Project"
DESKTOP_FILE="$PROJECT_FOLDER/NingandiGUI.desktop"
ICON_SOURCE="$PROJECT_FOLDER/project_images/Ningandi.png"
ICON_DEST="/usr/local/bin/Ningandi.png"
PROJECT_DEST="/usr/local/bin/Ningandi_Project"
EXECUTABLE_NAME="NingandiGUI.py" 
DNSMASQ_BACKUP="/etc/dnsmasq.conf.backup"
CURRENT_USER=$(whoami)
#Colors for text
RED='\x1b[31m'
GREEN='\x1b[32m'
YELLOW='\x1b[33m'
RS='\x1b[0m'

#Dynamically determine the correct user home path in case user tries using sudo on the install script
if [[ "$CURRENT_USER" != "root" ]]; then  
  USER_HOME="$HOME"
else
  USER_HOME="/home/$SUDO_USER"
fi

DESKTOP_DEST="$USER_HOME/.local/share/applications/NingandiGUI.desktop"    

#Array for domain variable this is to make the install dynamic and add more domains to it as needed
domains=(
"nintendo.net"
"conntest.nintendo.net"
"conntest.nintendowifi.net"
"nncs1.app.nintendowifi.net"
"nncs2.app.nintendowifi.net"
)

#Grab hotspot ip, I was considering turning it on but it seemed unesesarily intrusive & could cause issues also dificult to inplement for multiple distros
HOTSPOT_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
if [ -z "$HOTSPOT_IP" ]; then
  echo -e "${RED}Error: hostname -I returned an empty value, attempting fallback method...${RS}"
  HOTSPOT_IP=$(ip addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v 127.0.0.1 | head -1)
fi

#Give Error if this variable is empty meaning hotspot was off or nonexistent in current machine
if [ -z "$HOTSPOT_IP" ]; then
  echo -e "${RED}Error: Could not find hotspot IP address${RS}"     #Tell the user what went wrong, maybe make text red on the errors later. 
  echo -e "${YELLOW}Make sure your hotspot is active${RS}"          #The -e argument is for enabling escape codes, let the terminal interpret them in case you wondered
  exit 1
fi
echo "Found hotspot IP: $HOTSPOT_IP"

#Cleanly grab interface being used
HOTSPOT_INTERFACE=$(ip -o addr show | grep "$HOTSPOT_IP" | grep "^[0-9]" | awk '{print $2}' | tr -d ':' | head -1)
echo "Found interface: $HOTSPOT_INTERFACE" 

#Check if project folder exists before we start doing anything
if [ ! -d "$PROJECT_FOLDER" ]; then
  echo -e "${RED}Error: Ningandi_Project folder not found!${RS}"  #Let user know what went wrong 
  echo -e "${YELLOW}Make sure you ran this installation script from the exact folder you found it in${RS}"
  exit 1
fi

#Backup their dnsmasq.cong file just in case this way reverting to previous state is as simple as renaming a file, this will be part of uninstall script
sudo cp /etc/dnsmasq.conf "$DNSMASQ_BACKUP"
sudo cp /etc/dnsmasq.conf $USER_HOME/dnsmasq.conf-clean       #The first one is the backup this one is for using with the GUI

#Start loop appending the mapping configurations, this is why I made the array with the domains
echo "configuring DNS entries..."
for domain in "${domains[@]}"; do
  echo "address=/$domain/$HOTSPOT_IP" | sudo tee -a /etc/dnsmasq.conf  #tee -a appends the tring we piped in with echo at the end of the file
  echo -e "${GREEN}✅ Added $domain ${RS}"   #Nice visual feedback for the user, they see what has been added in real time
done 

#Edited version to use with the GUI 
sudo cp /etc/dnsmasq.conf $USER_HOME/dnsmasq.conf-edited

#Copy NingandiGUI.desktop file to applications
echo "Installing desktop file..."
sudo cp "$DESKTOP_FILE" "$DESKTOP_DEST"
sudo chmod 644 "${DESKTOP_DEST}"  #Give the user read and write permisions, group and others get read only, this prevents any issues with file permisions 

#Copy project folder to /usr/local/bin 
echo "Installing project files..."
sudo cp -r "$PROJECT_FOLDER" "$PROJECT_DEST"
sudo rm -f "$PROJECT_DEST"/*.ps1   #Globbed it because I may add more powershell scripts in this folder for Windows users and Linux users don't need those. 

#Copy icon to /usr/local/bin the icon needs to be here else some distros and DEs refuse to show it.
echo "Installing icon..."
sudo cp "$ICON_SOURCE" "$ICON_DEST"

#Make GUI program executable
echo "Setting permissions..."
sudo chmod +x "$PROJECT_DEST/$EXECUTABLE_NAME"

#Save the interface used to a config file for NingandiGUI to use
echo "Creating config file..."
echo "$HOTSPOT_INTERFACE" | sudo tee "${PROJECT_DEST}/interface.txt"
sudo chmod 644 "${PROJECT_DEST}/interface.txt"

#Give ownership to current user needs to be owned by user for it to show up in the apps list and dock else you get an ivisible icon
echo "Setting ownership..."
sudo chown -R $USER:$USER "$PROJECT_DEST" "$ICON_DEST"

#Final mesage letting the user know we are done here
echo -e "${GREEN}Installation complete!${RS}"
