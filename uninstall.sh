#!/bin/bash

#Variables to reuse same as the setup_install.sh
ICON_DEST="/usr/local/bin/Ningandi.png"
PROJECT_DEST="/usr/local/bin/Ningandi_Project" 
CURRENT_USER=$(whoami)
DNSMASQ_BACKUP="/etc/dnsmasq.conf.backup"
#Colors for text
RED='\x1b[31m'
GREEN='\x1b[32m'
YELLOW='\x1b[33m'
RS='\x1b[0m'
#Variable to determine the existence of files to uninstall dynamically
items_found=0 
#Dynamically determine the correct user home path in case user tries using sudo on the uninstall script
if [[ "$CURRENT_USER" != "root" ]]; then  
  USER_HOME="$HOME"
else
  USER_HOME="/home/$SUDO_USER"
fi
DESKTOP_DEST="$USER_HOME/.local/share/applications/NingandiGUI.desktop"  
#Check the existence of the project files and add 1 to item_found counter for each 
[ -f "$ICON_DEST" ] && ((items_found++))   #If the specific item is found we add 1 to the item counter
[ -d "$PROJECT_DEST" ] && ((items_found++))
[ -f "$DESKTOP_DEST" ] && ((items_found++))
[ -f "$DNSMASK_BACKUP" ] && ((items_found++))
[ -f "$USER_HOME/dnsmasq.conf-clean" ] && ((items_found++))
[ -f "$USER_HOME/dnsmasq.conf-edited" ] && ((items_found++))
#If no items found meaning the variable is 0 then we exit
if (( items_found == 0 )); then
  echo -e "${RED}Program not installed!${RS}"
  exit 1
fi

#Now we remove the items but we check each one is there first, this could be optimized since we already checked them but for now to keep it readable and maintainable we do it like this
if [ -f "$ICON_DEST" ]; then
  echo -e "${YELLOW}Uninstalling icon${RS}" 
  sudo rm "$ICON_DEST"
fi

if [ -d "$PROJECT_DEST" ]; then 
  echo -e "${YELLOW}Uninstalling project files${RS}"
  sudo rm -rf "$PROJECT_DEST"
fi

if [ -f "$DESKTOP_DEST" ]; then
  echo -e "${YELLOW}Uninstalling desktop file, apps shortcut${RS}"
  sudo rm "${DESKTOP_DEST}"
fi

if [ -f "$DNSMASQ_BACKUP" ]; then
  echo -e "${YELLOW}Restoring dnsmasq configurations${RS}"
  sudo cp "$DNSMASQ_BACKUP" /etc/dnsmasq.conf
  echo -e "${YELLOW}Removing configuration backup file${RS}"
  sudo rm "$DNSMASQ_BACKUP"
else
  echo -e "${RED}ERROR: Backup file not found at ${DNSMASQ_BACKUP}${RS}"
fi  

if [ -f "$USER_HOME/dnsmasq.conf-clean" ]; then
  echo -e "${YELLOW}Removing clean configuration file${RS}"
  sudo rm -f "$USER_HOME/dnsmasq.conf-clean" 
fi

if [ -f "$USER_HOME/dnsmasq.conf-edited" ]; then
  echo -e "${YELLOW}Removing edited configuration file${RS}"
  sudo rm -f "$USER_HOME/dnsmasq.conf-edited"
fi

echo -e "${GREEN}Uninstall process completed!${RS}"
