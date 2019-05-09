import shutil
from unittest import TestCase
import unittest
import smsh
import sys
import io
import os
import datetime
from unittest.mock import MagicMock

class help_menu_unit(TestCase):
    def setUp(self):
        pass

    def test_help_menu_unit(self):
        old_std_out = sys.stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        with self.assertRaises(SystemExit):
            smsh.help_menu()
        captured_output.seek(0)
        self.assertEqual(
            "\nsmsh.py, a CLI for sending SMS messages over an SSH interface with your phone" + "\n"
            + "\nBelow you will find a list of options to use when running this tool:" + "\n"
            + "-c or --config ->  Write a config file for the ssh connection." + "\n"
            + "  Format:  smsh.py -c IpAddress username portNumber timeout" + "\n"
            + "  Example: smsh.py -c 12.34.56.7 u0_a72 8022 10" + "\n"
            + "-s or --send   ->  Send an SMS text message." + "\n"
            + "  Format:  smsh.py -s PhoneNumber Message" + "\n"
            + "  Example: smsh.py -s 1234567890 Your Message" + "\n"
            + "-r or --read   ->  Read recent unread texts within your last 100 texts." + "\n"
            + "-b or --backup ->  Backup all texts onto your computer." + "\n"
            + "-o or --out    ->  Output a markdown text file each thread in the backup file." + "\n"
            + "-h or --help   ->  Displays this list of possible commands." + "\n",
        captured_output.read()
        )
        sys.stdout = old_std_out


class load_config_unit(TestCase):
    def setUp(self):
        pass

    def test_no_config_file(self):
        if os.path.exists(".config"):
            os.remove(".config")
        old_std_out = sys.stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        with self.assertRaises(SystemExit):
            smsh.load_config()
        captured_output.seek(0)
        self.assertEqual(
            ".config file not found or loaded incorrectly.\n"
            + "Try running with -c to write a config file and check that you are in the correct directory.\n"
            + "  Format:  smsh.py -c IpAddress username portNumber timeout\n"
            + "  Example: smsh.py -c 12.34.56.7 u0_a72 8022 10\n",
            captured_output.read()
        )
        sys.stdout = old_std_out

    def test_config_existing(self):
        # Ensure there is a config file
        argv = ["12.34.56.7", "u0_a72", "8022", "10"]
        with self.assertRaises(SystemExit):
            smsh.config(argv)
        smsh.load_config()
        self.assertEqual(smsh.config_dict["ssh_params"]["hostname"], "12.34.56.7")
        self.assertEqual(smsh.config_dict["ssh_params"]["username"], "u0_a72")
        self.assertEqual(smsh.config_dict["ssh_params"]["port"], "8022")
        self.assertEqual(smsh.config_dict["ssh_params"]["timeout"], 10)


class out_unit(TestCase):
    def setUp(self):
        pass

    def test_out_no_backup_file(self):
        if os.path.exists("./SMS_backup.json"):
            os.remove("./SMS_backup.json")
        old_std_out = sys.stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output

        now = datetime.datetime.now()
        path = os.getcwd() + "/" + "SMS_thread_out_" + now.strftime("%Y-%m-%d_%H-%M") + "/"
        shutil.rmtree(path, ignore_errors=True, onerror=None)

        with self.assertRaises(SystemExit):
            smsh.out()

        captured_output.seek(0)

        self.assertEqual(
            "Successfully created the directory " + path + " \n"
            + "Backup file not found. Try running smsh.py -b first to create a backup file in this directory.\n",
            captured_output.read()
        )
        shutil.rmtree(path, ignore_errors=True, onerror=None)
        sys.stdout = old_std_out

    def test_out_mkdir(self):
        pass
        # this test would check to see if dir is made correctly

    def test_out_simple(self):
        if os.path.exists("./SMS_backup.json"):
            os.remove("./SMS_backup.json")
        os.rename("./SMS_backup_small.json", "./SMS_backup.json")
        old_std_out = sys.stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output

        with self.assertRaises(SystemExit):
            smsh.out()

        os.rename("./SMS_backup.json", "./SMS_backup_small.json")
        captured_output.seek(0)

        now = datetime.datetime.now()
        path = os.getcwd() + "/" + "SMS_thread_out_" + now.strftime("%Y-%m-%d_%H-%M") + "/"
        sys.stdout = old_std_out

        self.assertTrue(os.path.exists(path + "1.md"))
        self.assertTrue(os.stat(path + "1.md").st_size != 0)

        self.assertTrue(os.path.exists(path + "2.md"))
        self.assertTrue(os.stat(path + "2.md").st_size != 0)

        self.assertTrue(os.path.exists(path + "3.md"))
        self.assertTrue(os.stat(path + "3.md").st_size != 0)

        shutil.rmtree(path, ignore_errors=True, onerror=None)


class ssh_command_unit(TestCase):
    def setUp(self):
        pass

    def test_failed_connection(self):
        # Ensure there is a config file, but it is not legitimate
        old_init = smsh.ssh_init
        smsh.ssh_init = MagicMock()
        argv = ["12.34.56.7", "u0_a72", "8022", "10"]
        with self.assertRaises(SystemExit):
            smsh.config(argv)
        smsh.load_config()
        old_std_out = sys.stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        with self.assertRaises(SystemExit):
            smsh.ssh_command("ls", "")
        captured_output.seek(0)
        self.assertEqual(
            "A communication error has occurred.\n"
            + "Check that your .config file has the same IPAddress\n"
            + "If this is your first time running this tool, make sure your computer connects to your phone via SSH.\n",
            captured_output.read()
        )
        smsh.ssh_init = old_init
        sys.stdout = old_std_out


class send_unit(TestCase):
    def setUp(self):
        pass

    def test_send_too_few_args(self):
        old_std_out = sys.stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        argv = ["1"]
        with self.assertRaises(SystemExit):
            smsh.send(argv)
        captured_output.seek(0)
        self.assertEqual(
            "Not enough arguments, try running with phone number, then message. For example:\n"
            + "smsh.py -s 1234567890 Your Message\nSends 'Your Message' to number 1234567890\n",
            captured_output.read()
        )
        sys.stdout = old_std_out
    def test_send_too_small_number(self):
        old_std_out = sys.stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        argv = ["1", "Hello", "World."]
        with self.assertRaises(SystemExit):
            smsh.send(argv)
        captured_output.seek(0)
        self.assertEqual(
            "Number is not formatted properly. Try inputting a 10 digit phone number numbers only. For example:\n"
            "smsh.py -s 1234567890 Your Message\nSends 'Your Message' to number 1234567890\n",
            captured_output.read()
        )
        sys.stdout = old_std_out
    def test_send_non_integer_number(self):
        old_std_out = sys.stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        argv = ["abcdefghij", "Hello", "World."]
        with self.assertRaises(SystemExit) as errMsg:
            smsh.send(argv)
        captured_output.seek(0)
        self.assertEqual(
            "Number is not formatted properly. Try inputting a 10 digit phone number numbers only. For example:\n"
            "smsh.py -s 1234567890 Your Message\nSends 'Your Message' to number 1234567890\n",
            captured_output.read()
        )
        self.assertEqual(errMsg.exception.code, 1)
        sys.stdout = old_std_out
    def test_send_message_too_long(self):
        old_std_out = sys.stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        argv = ["1234567890", "Hello", "World",
                "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaaaaaaaaaaaaaaa",
                "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaaaaaaaaaaaaaaa"]
        with self.assertRaises(SystemExit) as errMsg:
            smsh.send(argv)
        captured_output.seek(0)
        self.assertEqual(
            "Message is more than 160 characters. Android can only send single messages up to 160 characters.\n"
            "Please try sending a shorter message.\n",
            captured_output.read()
        )
        self.assertEqual(errMsg.exception.code, 1)
        sys.stdout = old_std_out

    def test_send_message_args(self):
        # Test that message is sending args correctly.
        old_init = smsh.ssh_init
        old_command = smsh.ssh_command
        old_close = smsh.ssh_close
        smsh.ssh_init = MagicMock()
        smsh.ssh_command = MagicMock()
        smsh.ssh_close = MagicMock()
        argv = ["1234567890", "Hello", "World"]
        with self.assertRaises(SystemExit) as errMsg:
            smsh.send(argv)
        smsh.ssh_command.assert_called_with("termux-sms-send -n 1234567890 Hello World",
                                            status_string="Sending a text message from your phone...")
        self.assertEqual(errMsg.exception.code, 0)
        smsh.ssh_init = old_init
        smsh.ssh_command = old_command
        smsh.ssh_close = old_close


class read_unit(TestCase):
    def test_read_happy(self):
        old_init = smsh.ssh_init
        old_command = smsh.ssh_command
        old_close = smsh.ssh_close
        old_retrieve = smsh.retrieve_file
        smsh.ssh_init = MagicMock()
        smsh.ssh_command = MagicMock()
        smsh.ssh_close = MagicMock()
        smsh.retrieve_file = MagicMock()

        path = os.getcwd() + "/SMS_last100/"
        try:
            os.mkdir(path)
        except OSError:
            pass
        now = datetime.datetime.now()
        path = path + now.strftime("%Y-%m-%d_%H-%M") + "_last100.json"
        f = open(path,"w+")
        f.write('[{"threadid": 1,"type": "inbox","read": false,"sender": '
                + '"Test1","number": "1234567890","received": "2019-04-25 14:02",'
                + '"body": "Hello"},'
                + '{"threadid": 1,"type": "inbox","read": false,'
                + '"number": "1234567890","received": "2019-04-25 14:02",'
                + '"body": "Hello"}]')
        f.close()
        with self.assertRaises(SystemExit) as errMsg:
            smsh.read()

        self.assertEqual(errMsg.exception.code, 0)
        smsh.ssh_command.assert_called_with("rm unread.json", "Removing temporary json file from phone.")
        smsh.retrieve_file.assert_called_with("/data/data/com.termux/files/home/unread.json", path)

        smsh.ssh_init = old_init
        smsh.ssh_command = old_command
        smsh.ssh_close = old_close
        smsh.retrieve_file = old_retrieve

class backup_unit(TestCase):
    def test_backup(self):
        old_init = smsh.ssh_init
        old_command = smsh.ssh_command
        old_close = smsh.ssh_close
        old_retrieve = smsh.retrieve_file
        smsh.ssh_init = MagicMock()
        smsh.ssh_command = MagicMock()
        smsh.ssh_close = MagicMock()
        smsh.retrieve_file = MagicMock()

        with self.assertRaises(SystemExit) as errMsg:
            smsh.backup()

        self.assertEqual(errMsg.exception.code, 0)
        file_string = os.getcwd() + "/SMS_backup.json"

        smsh.retrieve_file.assert_called_with("/data/data/com.termux/files/home/smsLog.json", file_string)
        smsh.ssh_command.assert_called_with("rm smsLog.json", "Removing temporary json file from phone.")

        smsh.ssh_init = old_init
        smsh.ssh_command = old_command
        smsh.ssh_close = old_close
        smsh.retrieve_file = old_retrieve



if __name__ == '__main__':
    unittest.main()
