#!/usr/bin/env python3

import sys
import paramiko
import datetime
import json
import os
import warnings
import yaml

# Remove cryptography warning that results from paramiko implementation.
warnings.filterwarnings(action='ignore', module='.*paramiko.*')


# Attempts to load the .config file which contains information on the ssh connection on the phone.
def load_config():
    try:
        with open(".config", 'r') as config_file:
            global config_dict
            config_dict = yaml.safe_load(config_file)
    except:
        print(".config file not found or loaded incorrectly.")
        print("Try running with -c to write a config file and check that you are in the correct directory.")
        print("  Format:  smsh.py -c IpAddress username portNumber timeout")
        print("  Example: smsh.py -c 12.34.56.7 u0_a72 8022 10")
        exit(1)


# Display a list of the possible commands a user could perform.
def help_menu():
    print("\nsmsh.py, a CLI for sending SMS messages over an SSH interface with your phone")
    print("\nBelow you will find a list of options to use when running this tool:")

    print("-c or --config ->  Write a config file for the ssh connection.")
    print("  Format:  smsh.py -c IpAddress username portNumber timeout")
    print("  Example: smsh.py -c 12.34.56.7 u0_a72 8022 10")

    print("-s or --send   ->  Send an SMS text message.")
    print("  Format:  smsh.py -s PhoneNumber Message")
    print("  Example: smsh.py -s 1234567890 Your Message")

    print("-r or --read   ->  Read recent unread texts within your last 100 texts.")
    print("-b or --backup ->  Backup all texts onto your computer.")
    print("-o or --out    ->  Output a markdown text file each thread in the backup file.")
    print("-h or --help   ->  Displays this list of possible commands.")

    # Exit with success code
    exit(0)


# Initialize the SSH client on the home computer.
def ssh_init():
    # Global variable storing the current ssh client
    global ssh_client
    ssh_client = paramiko.SSHClient()

    # Set the SSH client to auto accept unknown keys so that the shell is accepted by our client.
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the phone using values from the config file.
    ssh_client.connect(hostname=config_dict["ssh_params"]["hostname"], username=config_dict["ssh_params"]["username"],
                       port=config_dict["ssh_params"]["port"], timeout=config_dict["ssh_params"]["timeout"])


# Send a command over SSH and a display a status to users as it is working.
def ssh_command(command_string, status_string):
    try:
        # Send the command to the phone's SSH server.
        stdin, stdout, stderr = ssh_client.exec_command(command_string)

        # Print out a status for the user.
        print(status_string)
        print("If your process seems to hang, try opening the Termux app.")

        # Wait for the process to finish before moving on to the next step.
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("Commmands successfully run")
        else:
            print("Error", exit_status)
        return stdin, stdout, stderr
    except:
        print("A communication error has occurred.")
        print("Check that your .config file has the same IPAddress")
        print("If this is your first time running this tool, make sure your computer connects to your phone via SSH.")
        exit(1)

# Close the SSH connection.
def ssh_close():
    ssh_client.close()


# Retrieve a file from the remote server and write it on the local computer.
# Only works if ssh_client is already open.
def retrieve_file(remote_file_path, client_file_path):
    ftp_client = ssh_client.open_sftp()
    ftp_client.get(remote_file_path, client_file_path)
    ftp_client.close()

# Send a given message to a given phone number.
# This has a lot of user entry error checking, and it may be a bit overkill.
def send(argv):
    # Exit if there is not at least a phone number and a message.
    if len(argv) < 2:
        print("Not enough arguments, try running with phone number, then message. For example:")
        print("smsh.py -s 1234567890 Your Message\nSends 'Your Message' to number 1234567890")
        exit(1)

    # Check that the first argument is a valid phone number.
    # This may need to be changed to accomodate +1 and ()
    if (not argv[0].isdigit()) or len(argv[0]) != 10:
        print("Number is not formatted properly. Try inputting a 10 digit phone number numbers only. For example:")
        print("smsh.py -s 1234567890 Your Message\nSends 'Your Message' to number 1234567890")
        exit(1)

    # Recreate the message string from the remaining arguments.
    message_string = ' '.join(map(str, argv[1:]))

    # Check to make sure the message is a valid length.
    if len(message_string) > 160:
        print("Message is more than 160 characters. Android can only send single messages up to 160 characters.")
        print("Please try sending a shorter message.")
        exit(1)

    # Assemble the command string to send a message on the phone.
    command_string = "termux-sms-send -n " + argv[0] + " " + message_string

    # Send the actual command to the phone.
    ssh_init()
    ssh_command(command_string, status_string="Sending a text message from your phone...")
    ssh_close()

    # Print a "reassuring" completion message.
    print("Your message: \"" + message_string + "\" was sent.")
    # Exit with success code
    exit(0)


# Read the last 100 messages to check for any unread messages.
def read():

    # Make the name of the directory to store the message data.
    path = os.getcwd() + "/SMS_last100/"
    # Create the directory to store recent message data.
    try:
        os.mkdir(path)
    except OSError:
        pass
        # Directory already exists.
    else:
        print("Successfully created the directory SMS_last100")

    # Name the file of the last 100 messages.
    now = datetime.datetime.now()
    path = path + now.strftime("%Y-%m-%d_%H-%M") + "_last100.json"

    # Send the command to view the last 100 messages and save them to a json file.
    ssh_init()
    ssh_command("termux-sms-list -l 100 > unread.json", "Checking for unread messages...")

    # Retrieve the json file from the phone and delete it after it has been retrieved.
    print("Retrieving backup from phone.")
    retrieve_file("/data/data/com.termux/files/home/unread.json", path)
    ssh_command("rm unread.json", "Removing temporary json file from phone.")

    # Close the SSH session
    ssh_close()

    # Look for all the unread messages in the last 100 messages and print them.
    unread_messages = 0
    with open(path) as json_file:
        data = json.load(json_file)
        for p in data:
            if p["read"] == False:
                try:
                    print("- _" + p["sender"] + "_   " + p["received"])
                except:
                    print("- _Me_   " + p["received"])
                    pass
                print("  - " + p["body"])
                unread_messages = unread_messages + 1

    # Logic for the grammar of the unread messages.
    if unread_messages == 1:
        print("You have 1 unread message.")
    else:
        print("You have " + str(unread_messages) + " unread messages.")

    # Exit with success code
    exit(0)


# Back up all messages on the phone into the current directory for safekeeping.
def backup():
    # Create a helpful status message warning users that this takes a bit
    status_string = ("Backing up all text conversations on your phone."
                     + "\nThis could take awhile, relax and get a cup of coffee. :)")

    # Store all texts in a temporary backup file.
    ssh_init()
    ssh_command("termux-sms-list -l 999999999 -t all > smsLog.json", status_string)

    # Name the file.
    file_string = os.getcwd() + "/SMS_backup.json"

    # Retrieve the file from the phone.
    print("Retrieving backup from phone.")
    retrieve_file("/data/data/com.termux/files/home/smsLog.json", file_string)
    ssh_command("rm smsLog.json", "Removing temporary json file from phone.")

    # Close the SSH session
    ssh_close()
    print("Texts backed up in json file located at: " + file_string)

    # Exit with success code
    exit(0)


# Write the configuration file.
def config(argv):
    # Open the .config file.
    f = open("./.config", "w+")
    # Write the file in the format that we access it when it is loaded.
    f.writelines(yaml.dump({"ssh_params": {"hostname": str(argv[0]), "username": str(argv[1]),
                                           "port": str(argv[2]), "timeout": int(argv[3])}}))
    # Close the .config file.
    f.close()
    exit(0)


# Write out all threads into a folder denoting when it was created.
def out():
    # Compile the name of the folder to write to.
    now = datetime.datetime.now()
    path = os.getcwd() + "/" + "SMS_thread_out_" + now.strftime("%Y-%m-%d_%H-%M") + "/"

    # Attempt to make the folder.
    try:
        os.mkdir(path)
    except OSError:
        # Directory already exists.
        pass
    else:
        print("Successfully created the directory %s " % path)

    # Try to open the backup json file.
    try:
        with open(os.getcwd() + "/SMS_backup.json") as json_file:
            # Load the json from the file
            data = json.load(json_file)
            # Find the maximum ID so that we don't do more than that.
            maxKey = max([i["threadid"] for i in data])

            # Iterate through all keys.
            for x in range(maxKey):
                # Open a file to write any data found in the json file to.
                f = open(path + str(x) + ".md", "w+")

                # For all messages check if the thread number is the same as the loop thread number.
                for p in data:
                    if p["threadid"] == x:
                        try:
                            # If you sent the message indicate that.
                            if p["type"] == "sent":
                                f.write("- _Me_" + "  " + p["received"]+"\n")
                            # If someone sent you the message, indicate their name.
                            else:
                                f.write("- _" + p["sender"] + "_   " + p["received"] + "\n")
                            # Write the body of the message.
                            f.write("  - " + p["body"] + "\n\n")
                        except:
                            # If you sent and recieved the message, the recieved version will not have a sender.
                            # We do not want to print out this message twice.
                            pass

                # Close the file we are operating on.
                f.close()
                # Check if the file had anything written to it. If not, delete it.
                if os.stat(path + str(x) + ".md").st_size == 0:
                    if os.path.exists(path + str(x) + ".md"):
                        os.remove(path + str(x) + ".md")
    except:
        # If the backup is not found, notify the user.
        print("Backup file not found. Try running smsh.py -b first to create a backup file in this directory.")
        exit(1)
    # Exit successfully if all went well.
    exit(0)


# The main function. Takes in a list of arguments without the name of the program and performs a task.
def main(argv):

    # In the case of no arguments passed in ask users to read the help guide
    if len(argv) == 0:
        print('No arguments included, run "smsh.py -h" for a list of options')
        exit(1)

    # Check for the arguments that don't need to connect to the server on the phone.
    if argv[0] == "-c" or argv[0] == "--config":
        config(argv[1:])
    if argv[0] == "-o" or argv[0] == "--out":
        out()
    if argv[0] == "-h" or argv[0] == "--help":
        help_menu()

    # Load the config file to try to connect to the server on the phone.
    load_config()

    # Perform an argument that does need to connect to the server on the phone.
    if argv[0] == "-s" or argv[0] == "--send":
        send(argv[1:])
    if argv[0] == "-r" or argv[0] == "--read":
        read()
    if argv[0] == "-b" or argv[0] == "--backup":
        backup()

    # If no valid input is entered, ask the user to view the help guide.
    print('Not a valid argument combination, run "smsh.py -h" for a list of options.')
    exit(1)


# Check if the main function was called from the terminal. If so, call main().
if __name__ == "__main__":
    main(sys.argv[1:])
