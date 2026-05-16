CONNECT NINTENDO 3DS, NINTENDO SWITCH TO A WI-FI CONECTION WITH NO INTERNET ACCESS

## **📄INTRODUCTION**


The Nintgandi server is a personal connectivity validator that emulates Nintendo wifi checking servers it can trick nintendo consoles into thinking there is a valid internet connection, so you can use hotspot or wifi connections that have no actual internet without the console rejecting the connection. My server makes it so the console connects and stay connected to the access point and allow you to use things like FTP tools for file transfers or whatever homebrew app or tools that requires a local wireless connection without your nintendo device disconnecting and reconnecting constantly because the wifi has no internet (nintendo 3DS) or rejecting the connection outright because it has no internet (nintendo switch). I wrote this simple server because I wanted to use ftpd on my 3ds without internet, just a local hotspot and use it to transfer files using without having to remove the sd card from my 3ds, it also works on nintendo switch since it uses most of the same servers to validate  the wifi connection has internet and I added the additional domain to make it work on the nintendo switch.

I took the time to also code a nice gui app to control the Ningandi server called NingandiGUI, so you don't have to input a bunch of commands in the terminal every time you want to run the server all you have to do is set up the domain mapping once and from that point on use the gui app, it has 2 buttons, start server and stop server. the gui app will handle all the overhead and edge cases even if you accidentally close the gui window while the server was running the gui is coded to stop the server and restore normal DNS functionality and if you use CTRL + C on the terminal while the server was running the gui app will do the same handling any potential issues. 
You are free to use the server directly without the controller app but you have to remember to restore normal DNS functionality after you are done or you will have problems using internet on that machine later on if you wanted to add internet.
 
So, you want to use your pc hotspot without internet to use ftpd on 3ds or some other similar app on a modded switch? No problem, you can set up my server after mapping the nintendo domains to your your hotspot ip address or specific network interface to emulate the validation servers and the consoles will believe it has internet and stay connected. 


**How does the 3ds and Switch check for internet?**  
Based on my research which was mostly just niffing my network traffic using the 3ds and network monitoring tools:   
The console first looks up conntest.nintendowifi.net, then does a "GET /" with the "Host: conntest.nintendowifi.net" and the user-agent "CTR AC/02"  and expects a 200 response (ok) with the "X-Organization: Nintendo" header
then looks up both nncs1.app.nintendowifi.net, sends 5 packets of 16 NULL bytes to port 10025, then 5 packets of "\x00\x00\x00e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" and 5 packets of "\x00\x00\x00f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" to port 33334, and the same thing for nncs2.app.nintendowifi.net

The reasons why the connection fails and it disconnects constantly and reconnects as is the case with the 3ds or just doesn't allow you to connect at all like the nintendo switch does when you use a connection without internet is, when the consoles first looks up conntest.nintendowifi.net if it can't retrieve http://conntest.nintendowifi.net with user-agent "CTR AC/02" then the connection test will fail, if it returns a non-200 error code, then it will fail, if the IP returning the page is not "Nintendo" it will also fail, if when it looks up nncs1.app.nintendowifi.net and nncs2.app.nintendowifi.net, to send data on ports 33334 and 10025, if there is no response or not the correct data packet response then you guessed it, it will fail the connection test. 

My server will respond to those queries so all you have to do is map those addresses to your hotspot IP address using the configuration file on a DNS server you download and set the console's DNS setting for that specific network manually to be your hotspot IP address, after that your console believes there is a real internet connection, now you can use any apps that requires a local connection without internet such as FTPD on your console without having or needing internet. 

Can you run this server? (YES)
Any machine that has python installed can run this server, it's a flask server configured to respond to the queries made by the nintendo consoles, nothing special. 
what specs should your machine have: 
CPU: even a single core processor can run it so you need the minimum required by your OS and a little more for the server. 
RAM: about 512MB of ram is more than enough to run it so same thing, your OS minimum plus enough for the server. 
Disk space: enough for Python, Flask, and any other dependency downloaded, these are all small files any pc will have more than enough.
If you are running it on a VM just allocate enough resources to run the OS smoothly + the server. 
 
All you have to do is map the domains on the dnsmasq DNS server's config file to route them to your hotspot or preferred local wireless interface ip address, if you are using your computer's hotspot then route them to that ip address if you are using another application to make the wireless network then route them to whatever IP address that app or program uses.
I will mainly focus on linux distros, a specific few of them but you can use whatever OS you want, you can create a VM (virtual machine) and install Ubuntu or any other distro on it, preferably one of the listed distros. If you know how to configure a DNS server and already have one just download the dependencies listen on the [🔗TOOLS](#tools) section except dnsmasq, then just disable the default DNS client or service that may be bound to port 53 (check before disabling anything), and map the domains I mentioned and also listed on the [🔗TOOLS](#tools) section using your preferred DNS server to your hotspot's ip address and add that same address as the primary DNS server on the console's connection settings then start the Ningandi.py server and start the hotspot. If you don't know how to configure or use a DNS server then just set up a VM and set it up with Ubuntu and follow the tutorial or if you are already running a linux distro that is listed bellow, else just go to the [🔗TECHNICAL](#technical) section for steps on how to proceed.


**TLDR**


This tutorial mainly focuses on linux machines but the server can run on any machine with python installed, the reason for using linux is a one click installation process and to use the NingandiGUI.py program that handles a lot of overhead for you so I suggest installing a virtual machine with a linux distro of the ones listed in the tutorial I recommend Ubuntu, it is very user friendly and perfect for running a server or any other thing you may need a separate OS for so if you aren't on linux and don't want to install a virtual machine with a linux distro supported by my main tutorial then skip to the [🔗TECHNICAL](#technical) section for a quick rundown on how to use the server, note that it would be more convenient for you to install a VM with a linux distro because this allows you to use my gui program to restore normal DNS functionality after being done with the server, it also makes running the server super simple and easy, a simple click to start and stop it, if you use another OS you will have to handle the configuring the DNS yourself every time you want to run the server and stop it, so you will have to remember to set your default DNS back on to restore normal DNS functionality every time, not complicated but annoying.  

LIST of mentioned linux distros bellow: 

Ubuntu  
debian 
Linux Mint  
Elementary OS  
Pop!_OS  
Raspberry Pi OS  
Fedora  
RHEL    
CentOS  
Arch Linux  
Manjaro  
openSUSE  

Else install VM or go to [🔗TECHNICAL](#technical) section and skip to the section for your specific OS (yes I will repeat this a lot)  




## **📋TUTORIAL**


If you don't have a Linux OS installed then set up a VM and install a Linux OS image on it (I recommend Ubuntu) if you don't want to use a VM then skip to the [🔗TECHNICAL](#technical) section for your specific OS.  
[🪟WINDOWS 10/11](#windows-1011)    [🤖ANDROID](#android)    [🍎MAC OS](#mac-os)    [🐧LINUX](#linux) 


⚠**ATTENTION** dnsmasq by default having users:  
If your default DNS solution is dnsmasq you have to skip that specific download and after your setup is done read the extra step just for you bellow the uninstall section.


**Lets begin:**  
Open a terminal in the project folder that you downloaded and copy paste these commands based on your specific linux distro: 
(I even added the enterprise distros just in case) 


**Ubuntu, Debian, Linux Mint, Elementary OS, Pop!_OS, Raspberry Pi OS**

```
sudo apt update
sudo apt install -y dnsmasq
sudo apt install -y python3
sudo apt install -y python3-pip
sudo apt install -y python3-tk
sudo pip3 install flask
```


**Fedora, RHEL, CentOS**

```
sudo dnf update
sudo dnf install -y dnsmasq
sudo dnf install -y python3
sudo dnf install -y python3-pip
sudo dnf install -y python3-tkinter
sudo pip3 install flask
```


**Arch Linux, Manjaro**

```
sudo pacman -Syu
sudo pacman -S --noconfirm dnsmasq
sudo pacman -S --noconfirm python
sudo pacman -S --noconfirm python-pip
sudo pacman -S --noconfirm tk
pip install flask
```


**openSUSE**

```
sudo zypper refresh
sudo zypper install -y dnsmasq
sudo zypper install -y python3
sudo zypper install -y python3-pip
sudo zypper install -y python3-tk
sudo pip3 install flask
```



If your distro isn't on this list, use your specific distro's install command equivatents for these packages and then continue the tutorial in any case you can visit the [🐧LINUX](#linux)  tutorial in the [🔗TECHNICAL](#technical) section for details.


*"What did I just istall?"*

**python3**       
Python interpreter with it's standard libraries and supporting tools used to run programs coded in python

**python3-pip**   
Pip a package manager for python to download and install libraries and packages such as flask that we need for the server

**flask**         
Flask this is the web framework for python we get the core flask libraries and dependencies we need, my server is built with flask  

**dnsmasq**       
An easy to use and configure DNS and DHCP server, for our purposes I am using it to map the nintendo domains to your hotspot's ip address

**tkinter**       
Python library for creating GUIs (graphical user interface), this is what I used to make the gui program that manages DNS handling and operating the server for you.  


Could you have installed them all in a single line? Yes but I want you to see everything you are downloading and installing in your machine. If you know how to do it all in a single line on your specific package installer then go ahead.  
Now turn on the hotspot and run the setup_install.sh on a terminal that is in the project folder **while the hotspot is on**, else you get an error:  
```
bash ./setup_install.sh
```
*"Mama mia! an easy executable install? What is this Windows!?"* I made the script to automate the setup for you feel free to open the script in a text editor and see everything it does.  
Setup done! you even have an app icon in the apps feel free to add it to favorites to pin it on the dock but before you use it, read the next step to set up your console.


**CONSOLE SETUP:**  
Before you do anything you need to set up your console, in the DNS settings for the hotspot network wi-fi connection, manually set the hotspot's ip address as primary DNS server. Done!


**USAGE:**  
Open the NingandiGUI from the applications or dock if you already added it to favorites or search for it in the apps, it looks like a little silver 3ds-like console character smiling (tell me what you think of the look).  
click the Start server button you will see a warning telling you to turn OFF the hotspot, so turn it off if it's currently on, then once the server is started you will see it in the terminal  
now go ahead and turn on the hotspot, you are set! from now on all you do is open the NingandiGUI and it will handle restoring normal DNS functionality and getting rid of clinging processes by resetting your wifi once you are done so you can still use your internet normally after if you wanted to.  
once you are done using it just click the Stop server button or close the NingandiGUI window or press CTRL + C in the terminal, these are all handled by the NingandiGUI program even if the server was still running.  
⚠Make sure you reset your wi-fi manually if my GUI didn't reset it for you, just go to the wi-fi and turn it off and on, My gui program is meant to do it for you but it may not do it on some distros.



**UNINSTALL:**  
When you want to uninstall the project from your machine or simply change your setup to a new interface with more range etc, just run the uninstallation script I made  
on the terminal in the project folder containing the uninstall script run this:  
```
bash ./uninstall.hs
```
Done! it is uninstalled and if you want to install it again with your new setup just run the install script again and it will detect your new hardware and adapt automatically, it takes less than 10 seconds to uninstall and install again, easy peasy lemon squeezy!  



**People with dnsmasq as their default DNS solution**, every time you are done using the GUI program you need to start and enable dnsmasq manually in the terminal:  

```
sudo systemctl enable dnsmasq

sudo systemctl start dnsmasq
```

That's the way it must be the alternative had you do a bunch of commands but I added all that logic to the GUI so all you have to do is enable and start dnsmasq yourself after being done. (if you know how to code in python you can also go to the NingandiGUI.py that's in /usr/local/bin/Ningandi_Project/NingandiGUI.py and change the code by removing the lines that stop and disable dnsmasq in the stop server and closing function. that way you dont have to enable it and start it manually every time you are done using the server.)  


⚠**Do NOT close the terminal window** (X button at the top right of the terminal window) while the server is running. 




⚠**WARNING!**  
DO NOT force terminate the NingandiGUI program or the Ningandi server running in the terminal by using advanced commands, closing the terminal while the server is running to kill it, or with other programs like the system manager, just close it normally hitting the X in the GUI program or CTRL + C in the terminal, else you will have to do the DNS cleanup and process termination of potential zombie processes yourself by finding their PID and killing them manually, the commands to do this are:

```
ps aux | grep Ningandi  
```
(make note of the PIDs to kill them, the PID is the numbers next to the name)  
kill the Ningandi.py server and NingandiGUI.py if they appear in the list otherwise you are good, your distro allowed my closing function to go through so no action is needed.  
```
sudo kill -9 <PID> 
```
(do this with the PID of all the processes that were left running, kill then run the check again, then kill then check, etc, until only the grep result itself appears when you check)  
then restore your normal DNS client/solution:   
open the NingandiGUI program, start then server then close the GUI program (NOT the terminal, that will close itself)   
then check that dnsmasq is NOT listening to port 53 with this command:  
```
sudo lsof -i :53
``` 
Only your default DNS solution should be listening or nothing if you don't have one, if dnsmasq is listed then you skipped a step or your default DNS solution is dnsmasq in which case you're good since you started it manually before as you should've.  



This section was a lot longer explaining a plethora of commands and how to solve every single problem so I decided to add a lot of safeguards to the NingandiGUI program to solve almost any possible issues except for distro specific limitations that's where a lot of development time went to. If you run into any other issues let me know and I wil get to it and guide you as long as it's about this project and using the server, I will not respond to tech support messages unrelated to any of my projects or code unless we have an understanding beforehand, be reasonable.




## **⚙TECHNICAL** 

details for advanced users. In this section I won't be as pedantic as in the main [🔗TUTORIAL](#tutorial) section and may abstract away a lot of the basic steps you already know how to do.

This server can run on any device that is capable of running python and let's you use a DNS Server solution to map domains, so almost any machine, if you are planing to use an old modem as a local server without internet you can configure DNS on the modem to forward requests from the domains I listed to the computer or device running the server or use port forwarding to redirect connections to the device running the server's ip address note that my server is coded to listen to the all the network interfaces in the specific machine running it so you will need to redirect all the traffic in your network to the computer and use an ethernet cable so the server listens in on the eth0 interface, and set the console to use the router as the primary DNS server, you can do that in the 3ds and nintendo switch connection settings for the specific connection you saved, this all hinges on the modem having DNS configurations settings or port forwarding settings available, most default ISP modems don't but some of them can be flashed with custom firmware that does. 

I doubt anyone is going to use this method since it would require a pc anyway and doing this will limit your home server until you revert the changes, it is inconvenient to temporarily turn your modem into a dedicated nintendo validator server, it's easier and more convenient to simply use the computer's hotspot as the access point or use a powerful enterprise modem to run the server directly from the modem, expensive and extreme overkill for a quick file transfer or screen share between nintendo consoles and other devices. alternatively use the same exact method as the main tutorial and use an external network interface antenna and use that interface for the hotspot then let my installation script handle everything else, same effect as using your modem but cheaper and easier to do.





## **🤖ANDROID**

To run it on android phones you will need a rooted phone, a terminal emulator like Termux and install python on it and the dependencies then you need to map the domains to the phone's hotspot ip. You need root on your phone to route domains manually and also to be able to bind dnsmasq to port 53 which is something only possible with root, some apps provide workarounds for mapping addresses but these use tunneling which will only affect the phone itself and not the clients connecting to it. Root is mandatory to use the hotspot without having phone service so you'd need to root the phone anyway or use an app that let's you start a hotspot without phone network service, these are usually very limited apps and most modern smartphones stop you from starting a hotspot if there is no phone network service (this is a limitation imposed by the network providers not the manufacturer) besides the point, you cannot start the DNS server dnsmasq if you can't bind it to port 53 which as already mentioned is only possible with root if a service is already bound to it. if you overcome these hurdles just download the dependencies in the [🔗TOOLS](#tools) section using Termux and also download nano for convenience then identify what is your phone's DNS client/solver service to disable it if it's bound to port 53 (it varies from phone to phone, manufacturers and android versions) then map the domains in the dnsmasq config file using your hotspot ip address as the destination:

The basic rundown:  
1. install dependencies in the [🔗TOOLS](#tools) section + nano
2. map the domains to your hotspot ip by using nano or editing the file directly. type the command: nano /etc/dnsmasq.config  
then paste these at the end of the file using your hotspot ip address not my example address:   

```  
address=/nintendo.net/10.42.0.1 
address=/conntest.nintendo.net/10.42.0.1
address=/conntest.nintendowifi.net/10.42.0.1
address=/nncs1.app.nintendowifi.net/10.42.0.1
address=/nncs2.app.nintendowifi.net/10.42.0.1 
```

save it and close nano.  

3. Use the hotspot's ip address in the consoles primary DNS setting on the hotspot network connection settings   
4. Identify what service is bound to port 53 to kill it/disable it temporarily  
Check if port 53 is available:
``` 
netstat -tuln | grep :53
```
5. stop then disable the service that is bound to port 53 and start dnsmasq
(if you can't disable it or don't know a way to do it yourself try running dnsmasq anyway and see if it gives you an error, it may actually take over port 53 anyway on some devices, worth trying)  
6. start the server: 
```
python3 Ningandi.py
```
7. turn on the hotspot and it will make the console think it has internet
8. Once done with the server stop it then stop and disable dnsmasq
9. Enable then start whatever service was bound to port 53 if any  
   
For future uses just repeat steps 5 to 9  
    

**NOTES:**    
I know that I wasn't specific and abstracted away a lot of the steps, that's because as already mentioned the services that could bind to port 53 on android, whatever DNS solution your specific phone uses varies by versions and manufacturers as an advanced user I expect you to be able to identify them if there is any service bound to port 53 and disable them I may add specific steps for each phone in the future but it will be a limited list of phones I personally have and use for developing apps and experimenting, if you want to contribute to this section feel free to send me details about your specific setup/method to run the server and map the domains especially the manufacturer, model and DNS solver orservice that bound itself to port 53 if there was one for your phone and I will add them to the list with your method.
 
**DO NOT USE THE NingandiGUI.py PROGRAM** (even if you get it to run somehow, it won't work for you)





## **🪟WINDOWS 10/11**


**Explaining limitations:**  
On windows it is too complicated for a simple tutorial or quick install script, Microsoft really loves setting artificial limitations just to make your life harder, for windows it involves either using WSL2, and because it is a garbage hyper-V image poorly set up by Microsoft, it's very limited, isolated from the windows host and on a different network layer you need to configure network bridging very complex, or expose the DNS server running in WSL2 to the windows network and that's also too complicated my head already hurts just thinking of ways to make it tutorial friendly let alone make it possible at all (I'm just angry at Microsoft but WSL2 is not bad for quick tests), not an easy copy paste on terminal kind of guide, the other method is using the available DNS servers for windows that are not as user friendly or as easy to use as dnsmasq, with some of them requiring you to prepare different config files or enter complicated setup web pages and it's overkill anyway just to map some domains to the hotspot ip address so that the server can respond to queries from clients connected to the hotspot. For a smooth quick install and user experience you need to set up VM with a linux distro image, I recommend Ubuntu and then just go to the main tutorial, after the VM is set up it takes a couple minutes to follow the main tutorial, otherwise keep reading. I know you probably skipped to down to this section because you wanted to avoid setting up a VM but it's literally the simplest and most elegant solution that requires the least amount of effort, steps, and knowledge so even though it is very doable in windows but not without Microsoft trying to stop you at every turn, it seemed unreasonable and if you are willing to go through the gauntlet that is the windows setup, continue reading.


If you are an expert you probably already know exactly what to do just from reading the [🔗INTRODUCTION](#introduction) section but believe me you will need help anyway this took me days of testing tools, different DNS servers, and working with windows settings even to the point of making a few scripts to get it working then scraping them and making new ones etc. Of all the DNS servers that I tested, I found Technitium DNS Server to be the easiest to use even though after you see what you actually have to do, you will be like "you call this easy to use?" trust me it is the easiest one to use that works well, and don't worry I will provide you everything you need I went through the gauntlet for you, all you have to do is follow my steps and it'll be smooth sailing.  
The first thing you need to do install dependencies

**Dependencies & setup:**  
download this project  
go to python.org and get the latest version of python   
Install it selecting the advanced options checking all the boxes except the ones that download additional things   
press the Windows + X buttons (or right click the start button) and select Terminal(Admin)   
in the Powershell terminal:   
```
python.exe -m pip install --upgrade pip  
pip install flask   
```
now go to technitium.com and download Technitium DNS Server and install it   
make it your default DNS Server when it asks you to (don't worry you'll turn it off later when you aren't using it anymore)   
now we need to do the mapping on Technitium so open your browser (no internet needed for this step) and in the URL go to: 127.0.0.1:5380    
it will ask you to set a user and password set something simple like admin and admin   


**Now we start mapping:**  
go to the Zones tab and press the Add Zone button in the far right  
in the Zone name you will set nintendo.net and leave it as primary zone hit add, now hit the Add Record button and in the IPv4 section put in your hotspot ip address 192.168.137.1 leave everything else blank and hit save  
now hit the back button in the top left  
add a new zone and name it conntest.nintendo.net leave it as primary zone, hit add, hit Add record, set your hotspot ip in the IPv4 section 192.168.137.1 leave everything else blank and save  
now hit the back button in the top left  
add a new zone and name it conntest.nintendowifi.net leave it as primary zone, hit add, hit Add record, set your hotspot ip in the IPv4 section 192.168.137.1 leave everything else blank and save  
now hit the back button in the top left  
add a new zone and name it nncs1.app.nintendowifi.net leave it as primary zone, hit add, hit Add record, set your hotspot ip in the IPv4 section 192.168.137.1 leave everything else blank and save  
now hit the back button in the top left  
add a new zone and name it nncs2.app.nintendowifi.net leave it as primary zone, hit add, hit Add record, set your hotspot ip in the IPv4 section 192.168.137.1 leave everything else blank and save  

Done! (figuring this out was not easy and yet it's the easiest one to use)


**Hotspot setup:**  
now we have to bypass the Windows artificial limitation that requires you to have internet to let you use the hotspot:  
"but Windows11 won't let me use my hotspot without internet!" I got you fam, I made a powershell script that will bypass this limitation but it requires creating a loopback network adapter  
open the device manager, in the action tab select Add legacy hardware then in the setup wizard select install the hardware manually (advanced), now you need to select Network adapter, then Microsoft and in there look for the loopback adapter, Microsoft KM-TEST Loopback Adapter  
after the adapter is done installing we need to set it up, open the control panel, go to Network and Internet, then Network and Sharing Center, then in the options to the left select change adapter settings, your new loopback adapter should be there probably named something like Ethernet 2  
right click the loopback adapter and select properties double click on Internet Protocol Version 4 (TCP/IPv4), now in the ip address tab set something like 192.168.1.1 and the subnet mask 255.255.255.0 then hit ok  
Now make sure the loopback adapter is enabled right click it and if there is an option "Enable" click it otherwise it's already enabled  
go back to the powershell terminal  
Now we need to create 2 new rules on the firewall to allow the Ningandi.py server and Technitium DNS Server to work:  
```
New-NetFirewallRule -DisplayName "DNS Server" -Direction Inbound -Action Allow -Protocol UDP -LocalPort 53; New-NetFirewallRule -DisplayName "HTTP Server" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 80
```
make note of the names I set for these rules "DNS Server" and "HTTP Server" for if you want to disable/enable them later on your firewall settings  

Now in the powershell terminal change directories to the project folder:  
cd C:\Users\\<your username\>\Desktop\Ningandi\Ningandi_Project (this is an example as if you had it in your desktop, use the actual path with your actual user name)  
Now to run powershell scripts you probably need to set permission so I will give you a command that will temporarily allow you to do it for the duration of the session, setting it permanently is not safe just use the command every time and play it safe:  
```
set-executionpolicy -executionpolicy Bypass -scope process
```
now we start the hotspot with the script:

```
./hotspot-start.ps1 on
```

now we start the Ningandi server:

```
python ./Ningandi.py

```


**Console setup**   
now in your console set the hotspot wifi network and in the DNS section set it manually, use the hotspot ip address as primary DNS server example: 192.168.137.1   
Done you will see it working in the terminal, the console thinks it has internet and you are free to use any local wi-fi tool like FTP apps without your console needing internet   

**After you are done**  
After you are done using the server you can just hit CTRl+C in the terminal to end it and in your tray you can right click Technitium and hit Service then Stop, your PC has normal connectivity again    
the hotspot can be turned off from the normal Windows settings or with this command in the powershell terminal:   
```
./hotspot-start.ps1 off
```


**Usage Framework:**   
start Technitium and on the system tray right click Technitium and make sure in Network DNS that Technitium is selected    
open an admin PowerShell terminal and change directory to the project folder where you placed it, example: cd C:\Users\\<your username\>\Desktop\Ningandi\Ningandi_Project  
enter the command to allow scripts:   
```
set-executionpolicy -executionpolicy Bypass -scope process
```

start hotspot:  
```
./hotspot-start.ps1 on
```
start server:  
```
python ./Ningandi.py
```
when you are done just hit Ctrl + C in the terminal and then stop the hotspot
```
./hotspot-start.ps1 off
```
then stop Technitium in the system tray by right clicking it and hiting Service then Stop 


**WSL2**
I won't even bother with WSL2 because at that point you are just running a limited Linux Hyper-V environment on your windows machine and you'd do better just following the steps bellow:  

1. Install a VM with Ubuntu.
2. Follow the main [🔗TUTORIAL](#tutorial) section.
3. I had to make that joke sorry (seriously you will probably enjoy linux if you are resorting to WSL2 for this kind of task)
 

**NOTES:**  
*"This took you days to figure out on windows? HA!"* Yes it did I mainly work on Linux and do most of my coding and projects on Linux, not being familiar with windows 11 Home edition artificial walls and limitations was an issue, especially since I mostly use enterprise editions on Windows  
having to look for solutions at every turn was not simple, testing a lot of software to see if it was viable and coding tools that later became irrelevant or even useless after finding another windows artificial limitation and seeing that tools I was using and counting on were not available for home version users, and having to scrap them then start over again, it took a long time, I was considering making an easy install.exe program that automated everything like I did for Linux but that was just the scope creep talking since it seemed difficult to implement in hindsight, so I decided to just make the tutorial as easy as possible, picking the best DNS server and making sure it all runs smoothly.   
Before anyone asks, I didn't use netsh for the hotspot workaround because it's very old and barely held together with ductape by now, it's been deprecated and doesn't work well with recent drivers so most users would've had to do complex driver setups on their systems to get it working, I went with a more pragmatic approach of creating a powershell script that bypasses the hotspot start limitations after seting up a loopback interface.    
If you want to make an install program to automate this entire process or the setup and help out other Windows users let me know, it shouldn't be too difficult to implement with the framework I laid out if we do it together.  



**DO NOT USE the NingandiGUI.py PROGRAM** (it won't work in windows)   
**DO NOT RUN the setup_install.sh or uninstall.sh** (it's linux users only)     




## **🍎MAC OS**  

you need a workaround to use your hotspot without internet, this project by zhuhuilin will help you with that:  
```
https://gist.github.com/zhuhuilin/01656866b3e73a677a434c21183b40d2
```

On mac pc it's the same process install python3 and dependencies (listed in the [🔗TOOLS](#tools) section) and map the domains, so open a terminal and do this:

install Homebrew package manager  
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
Then install the dependencies:
```
brew install python3 flask dnsmasq
```
Now we edit the dnsmasq config file to map domains to your hotspot's ip address:  
```
sudo nano $(brew --prefix)/etc/dnsmasq.conf
```
then paste these entries at the end of the file  
```
address=/nintendo.net/172.20.10.1
address=/conntest.nintendo.net/172.20.10.1
address=/conntest.nintendowifi.net/172.20.10.1
address=/nncs1.app.nintendowifi.net/172.20.10.1
address=/nncs2.app.nintendowifi.net/172.20.10.1
```
then press CTRL+O, then Enter, then CTRL+X  
in your console's connection setting for the hotspot connection, manually set the primary DNS settings be your hotspot's ip address 172.20.10.1   
check that only dnsmasq is listening to port 53 with this command  
```
sudo lsof -i :53
```
if that shows nothing or dnsmasq is listed you are good to go otherwise stop then disable whatever is bound to port 53 temporarily so dnsmasq can take over (unlikely scenario)  
start dnsmasq if not already running:  
```
sudo brew services start dnsmasq
```
go to the project folder sub folder named Ningandi_Project and open a terminal if not already there or open a terminal and drag the folder to the terminal same effect:
```
sudo python3 Ningandi.py
```
Now set up is done start your Mac hotspot, then start the server and the console will now think it has internet.  
when you are done just CTRL + C in the terminal window to stop the server then stop and also disable dnsmasq and re-enable then start whatever service you may have disabled before (unlikely).  
```
sudo brew services stop dnsmasq
sudo brew services disable dnsmasq
```
use the command to re-enable and start whatever you may have disabled and stopped before to free port 53  

**Recap:**   
after you are setup it is simple to use:  

**Start server:**   
\===================================================================   
Open terminal in the project folder sub folder Ningandi_Project or drag the folder to the terminal same effect  
```
sudo brew services enable dnsmasq
sudo brew services start dnsmasq
sudo python3 Ningandi.py
```
Turn your hotspot on  


**Stop server:**   
\===================================================================  
Press CTRL + C on the terminal window  
```
sudo brew services stop dnsmasq
sudo brew services disable dnsmasq
```
turn off hotspot (turn wifi off and on again, this gets rid of any clinging dnsmasq processes)  


**Notes:**  
I need feedback from the 1 MacOS user that will use my project if you encounter any road blocks let me know  
I can make a script to automate the start and stop process but I believe it's unlikely that anyone using a mac pc will even use my tool in case I am wrong request it and I will add it


**DO NOT USE THE NingandiGUI PROGRAM** (It won't work on Mac OS even if you get it to run)  
**DO NOT RUN the setup_install.sh** (it's for linux users only)  




## **🐧LINUX**  

If your distro wasn't listed  
Check what is your default DNS solution.  
Is your default DNS solution systemd-resolved, named, knotd, pdns_recursor, dnsmasq or unbound?   
YES: Then go to the [🔗TUTORIAL](#tutorial) section download the programs listed using your distro's equivalent commands and follow along with the main [🔗TUTORIAL](#tutorial)   
NO: Then check if port 53 is bound by your DNS solution:  
Command:  

```
sudo lsof -i :53
```

Was anything listed?  
NO? Go to main tutorial download all dependencies using your distro equivalents commands and follow the main [🔗TUTORIAL](#tutorial) section  
YES? disable if needed with command bellow: replace \<service name\> with the actual name of the DNS service (also send me a mesage with the DNS service name to add it to the code for support)  

```
sudo systemctl stop <service name>
sudo systemctl disable <service name>
```

now go follow the main [🔗TUTORIAL](#tutorial) but every time after you are done with the NingandiGUI you need to re enable your default DNS solution

```
sudo systemctl enable <service name>
sudo systemctl start <service name> 
```

You need to do that every time until you tell me the DNS solution name so I can add it to the code so your usage framework is:

```
sudo systemctl stop <service name>
sudo systemctl disable <service name>
``` 
start the NingandiGUI from the apps list and use it but after you are done:
```
sudo systemctl enable <service name>
sudo systemctl start <service name> 
```


**💻Manual labor for experts🤓:**

If you want to operate it manually and not use my NingandiGUI program or my easy installation script setup_install.sh because you dont wan't a new app shortcut, follow along:

1. Install dependencies (they are in the [🔗TOOLS](#tools) section the exact install commands are in the main [🔗TUTORIAL](#tutorial) also)
2. Make a copy of your current dnsmasq.conf file:
```
sudo cp /etc/dnsmasq.conf ~/dnsmasq.conf-clean
```
3. Add these entries to the dnsmasq.config file using your computer's hotspot ip:
```
sudo nano /etc/dnsmasq.conf
```
paste these entries to the bottom of the file, CTRL + END, then paste them (make sure to use your actual hotspot's ip address)

```
address=/nintendo.net/<your.hotspot.ip>  
address=/conntest.nintendo.net/<your.hotspot.ip> 
address=/conntest.nintendowifi.net/<your.hotspot.ip> 
address=/nncs1.app.nintendowifi.net/<your.hotspot.ip> 
address=/nncs2.app.nintendowifi.net/<your.hotspot.ip> 
```

press CTRL + O, then ENTER, then CTRL + X.

4. Make a copy of the edited dnsmasq.conf file (you can probably see where this whole process is going already)
```
sudo cp /etc/dnsmasq.conf ~/dnsmasq.conf-edited
```
5. You need to restart dnsmasq but because dnsmasq tends to stay on, clinging to your network interface even after stopping it you need to stop it then turn your wifi off and on again then start it again, this is the easiest way to do it traditional restart commands don't work in my experience it just gives you an error because dnsmasq stayed on and bound to port 53 (may vary from distro to distro)
```
sudo systemctl stop dnsmasq
```
turn your wifi off and on again
```
sudo systemctl start dnsmasq
```
We do this to reset dnsmasq and make the configurations get updated

6. Run server and start hotspot
   To start server open terminal on project folder sub folder named Ningandi_Project:
```
sudo python3 Ningandi.py
```
7. Set up the console's wifi connection DNS server settings, set it manually using your hotspot's ip address as primary DNS the rest leave as automatic.(this step could be done at any point)
Now the console believes it has internet.
8. After you are done using the server use CTRL + C in the terminal to stop it and then stop dnsmasq
```
sudo systemctl stop dnsmasq
```
9. Restore normal DNS functionality by swabbing the dnsmasq.conf file with the clean one
```
sudo cp ~/dnsmasq.conf-clean /etc/dnsmasq.conf
```
10. Turn your wifi off and on again

11. Start dnsmasq:
```
sudo systemctl start dnsmasq
```
Done your DNS functionality is restored you may use your internet if you want

For future uses just swap the dnsmasq.conf file with the edited one then reset dnsmasq before starting the server then the hotspot
and after being done stop the server, swap the dnsmasq.conf file with the clean one and reset dnsmasq. 

**USAGE**  
**Start Server:**  
\================================================  
```
sudo cp ~/dnsmasq.conf-edited /etc/dnsmasq.conf
sudo systemctl stop dnsmasq
```
reset your wifi
```
sudo systemctl start dnsmasq
```
then start the server: 
```
sudo python3 ningandi.py
```
turn on hotspot

**Stop Server:**  
\================================================   
CTRL + C in the server terminal window to stop it  
```
sudo cp ~/dnsmasq.conf-clean /etc/dnsmasq.conf
sudo systemctl stop dnsmasq
```
reset your wifi
```
sudo systemctl start dnsmasq
```

**Notes:**  
You can make a simple program to automate the start and stop server functions using the framework I laid out for you, alternatively you can just follow The main [🔗TUTORIAL](#tutorial) and use the NingandiGUI program which does all this and much more for you.



## **🛠TOOLS**
general reference to the dependencies to install and domains that wil be mapped  

**dependencies to install on your machine to run the server are:**  
```
python3                  All OSes
python3-pip              All OSes
flask                    All OSes
dnsmasq                  Linux, MacOS, Android
Homebrew                 MacOS
Technitium DNS Server    Windows
Nano                     Android
```

**The domains to map:**  
```
nintendo.net
conntest.nintendo.net
conntest.nintendowifi.net
nncs1.app.nintendowifi.net
nncs2.app.nintendowifi.net
```


## **⚖LEGAL**  
This project in NOT affiliated with, endorsed by or associated with Nintendo, Nintendo 3ds, Nintendo Switch, and other Nintendo products names and trademarks of Nintendo, Inc.  
This project is an independent tool created to solve connectivity issues on local networks I am NOT reverse engineering or circumventing any security measures I am just responding to local network requests  
This tool is for personal, noncommercial use on networks that you either own or have permission to use.  
You will assume all responsibility for how you use this tool.  




## **💭FINAL THOUGHTS**  
I mostly code in C, C++, Python, Shell script, and powershell scripts, decided to make this project almost entirely in python to make it easier on myself to do, but working with tkinter (*"tkinter!? what is this the 90s?"*) you'd be surprised by how good some GUIs can look on it, anyway it was a pain and figuring out creative ways to handle all potential issues took me a lot longer than I thought, you may look at my code and say *"duh how else would you do it?"* but hindsight is always 20/20 and I dont always see the obvious solution until later.   
Feel free to use the code as you need it, learn from it, use it as educational material (not to cheat on your CS class) to study, make derivatives works or contribute to the code read the licence document for details. I left all my notes as I was coding in, so it's clear what everything does (mostly meant for future me). The code itself is basic networking for the Ningandi.py server and for the NingandiGUI.py It's mostly functions to check what your system is using and apply that to the start, stop, and closing functions and a lot of tkinter settings to make it look "good", that's what took me the most time since I don't normally make gui applications most of my work focuses on backend programing, I also made an installation scrip and uninstall script. If you find any issues or have opinions on what would look better or how to improve something let me know.  
I hope the Nintendo modding communities especially the 3DS communities find use out of this I just wanted to give back to the communities that I got so much out of so I poured all my effort into making my private tool into an actual usable project people can use withouth them needing to be a network engineer to operate it, I also plan to add compatibility for any future Nintendo console that uses a different servers to validate wi-fi and add more detailed tutorials in the [🔗TECHNICAL](#technical) section for different devices and edge cases as needed/requested.  

If this project is well recieved by anyone that actually uses it I will make sure to publish more of my tools that I've created after making them user friendy and creating tutorials and GUIs for them otherwise I'll just step back and keep my other tools and code for consoles private.