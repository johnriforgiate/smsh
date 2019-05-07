from unittest import TestCase
import unittest
import smsh
import sys
import io
import os


class helpMenuUnit(TestCase):
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

class loadConfigUnit(TestCase):
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




if __name__ == '__main__':
    unittest.main()