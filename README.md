## SMSH ##
### A command line texting tool ###
This was developed as a senior project at Kansas State University.
- Requirements:
  - Android phone
  - Mac or Linux OS
  - Old version of Termux and Termux:API
  - Python 3
  - Patience
  
### Setup ###
To run this tool, you must be able to SSH into your phone from your computer.
I followed the steps outlined in this video to setup the ssh client.

https://www.youtube.com/watch?v=RxZRmKv-F94

Use the -c command to write a config file for the ssh connection.
Format:  smsh.py -c IpAddress username portNumber timeout")
Example: smsh.py -c 12.34.56.7 u0_a72 8022 10")

### Dependencies ###
Some of these may already be packaged with your version of Python 3
- sys
- paramiko
- datetime
- json
- os
- warnings
- yaml

### Usage ###
Can be used to:
- Send an SMS text message.
- Read recent unread texts within your last 100 texts.
- Backup all texts on your phone onto your computer.
- Output a markdown text file each thread in the backup file.
