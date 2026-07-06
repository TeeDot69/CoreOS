# CoreOS
Basic cli python program made to act like an Operating System

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Commands](#commands)
- [Docs](#docs)
    - [Importing Commands](#importing-commands)
    - [Importing Programs](#importing-programs)

# Overview
CoreOS is fairly basic out of the box it includes 

- Command Line (Obviously)
- Package Registry
- User Accounts with Permissions
- Filesystem (in theory)
- Text Editor
- Few other utilities and Programs

## Main Screen (or whatever you want to call it)

This might remind you a bit of Linux.

<p>
  <img width="889" height="577" alt="Screenshot 2026-07-05 202304" src="https://github.com/user-attachments/assets/8aa26662-c5ee-4583-bbdc-55f7294baf2a" />
</p>

## Sysfetch

This is kind of like Neofetch/Fastfetch, but I made it and I'm better. (Okay, I might be lying—some things may not work.)

<p>
  <img width="692" height="422" alt="Screenshot 2026-07-05 202331" src="https://github.com/user-attachments/assets/35e5c8c5-74e5-4bea-aeda-719b8a379129" />
</p>

## User Accounts

### Adding a User

<p>
  <img width="306" height="36" alt="image" src="https://github.com/user-attachments/assets/24fb4af7-f8d7-414b-8682-a661e54507aa" />
</p>

### Removing a User

<p>
  <img width="291" height="53" alt="image" src="https://github.com/user-attachments/assets/0352303c-a73d-4b7a-a871-a8eec1fe1ebf" />
</p>

## Diskinfo

<p>
  <img width="402" height="69" alt="image" src="https://github.com/user-attachments/assets/8d43e3d5-6d1c-4d3d-bdc5-0b076306aeda" />
</p>

## Monitor

<p>
  <img width="342" height="118" alt="image" src="https://github.com/user-attachments/assets/d2257f38-c4f9-4e91-a683-9ea90802f361" />
</p>
Very basic at the moment.

## Calculator

<p>
  <img width="498" height="138" alt="image" src="https://github.com/user-attachments/assets/5e320e5b-7365-4581-b66b-1354b4580612" />
</p>

## Edit 
<p>
  <img width="636" height="380" alt="image" src="https://github.com/user-attachments/assets/16cefd60-a5e7-4725-94fb-67622ee17b22" />
</p>

# Prerequisites
You will need to Download and Install Python 3.8 at the earliest and preferably use 3.13.5, 3.11.X or 3.12.2
CoreOS works on Windows and Linux Fully aswell as Termux on Android however some things may not work such as hardware detection 

# Setup
Head over the Releases Tab and Download the .zip file for the Latest Release
Once you have downloaded it Extract the Zip File, you may place the CoreOS folder anywhere but to make it easier place it at the root of your primary drive (or a external drive), on the desktop or in your Operating Systems personal user folder.
You may also add entries in the Windows Start Menu or whatever your operating systems application launcher is 

# Commands
These are the list of commands with their usage and what they are 
(a lot of these may remind you of linux clear and cls both do the same thing and both work on windows
```
adduser      - adduser <name> <password> [-su] - Create user
cat          - cat <file> - Print file contents
cd           - cd [directory] - Change directory
clear        - Clear screen (Windows: cls)
cls          - Clear screen
copy         - copy <source> <destination> - Copy file
date         - Print current date (ISO format)
echo         - echo <text> - Print text
env          - Print CoreOS environment variables
exit         - Exit CoreOS
find         - find [directory] - Find files and directories
grep         - grep <pattern> <file> - Search file for pattern
head         - head <file> - Print first 10 lines
help         - Show this help message
history      - Show command history
logout       - Logout current user and return to login prompt
ls           - ls [directory] - List directory contents
mk           - mk <filename> - Create empty file
mkdir        - mkdir <directory> - Create directory
mv           - mv <source> <destination> - Move/rename file
programs     - List all available programs
pwd          - Print working directory
remuser      - remuser <name> - Remove user
rm           - rm <file> - Remove file
rmdir        - rmdir <directory> - Remove empty directory
sort         - sort <file> - Print sorted lines
su           - su [username] - Switch user with password prompt
sudo         - sudo <command> - Run with elevated privileges
sysfetch     - Display system information
tail         - tail <file> - Print last 10 lines
time         - Print current time
tree         - tree [directory] - Display directory tree
uname        - Print system information
wc           - wc <file> - Count lines in file
wget         - wget <url> [dest] - Download file
whoami       - Print current username
```

# Docs
Here's some docs for things such as Importing your own commands


## Importing Commands
Commands can be any Python script or file running them does not require adding a file extension to run in the command line and you can just run via name (command.py is just "command") script files (mainly batch and .sh) also work by running "./filename.extension"
Any python script or command in theory should be compatible althought some advanced may not be 
Commands are placed into the Commands folder and are interpeted and executed by Command.py they can be ran from anywhere, as opposed to needing to be in the same directory.

## Importing Programs
Programs work very similar to commands any python files however you can also add package info which includes name and version **this is __NOT__ required** for them to work but it allows the OS to automatically pick them up 
to add package info add these lines to the top of the file after imports
```
PKGNAME = "name goes here" # a prefered format is developer.programname or just programname please don't use spaces
PKGVER = "x.x"
```
Programs are placed into the Programs folder and can be any .py file in there aswell as any subfolders.

The main difference between Programs and Commands are Programs are interactive usually and more advanced and Commands are Basic Instructions programs can work like commands sometimes (like a program being ran like a command), however commands are usually not interactive in the same way

for example running Edit will clear the screen and take up the whole thing it has its own prompt for commands however running Cat test.txt will perform the instruction to display contents and then bring you back to a prompt


