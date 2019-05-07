from unittest import TestCase
import smsh
import sys
import io


class unit_test(TestCase):
    def setUp(self):
        pass

    def test_help_menu(self):
        old_std_out = sys.stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        smsh.help_menu()
        captured_output.seek(0)
        self.assertEqual(
            captured_output.read(),
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
            + "-h or --help   ->  Displays this list of possible commands." + "\n"
        )
        sys.stdout = old_std_out

if __name__ == '__main__':
    unittest.main()
