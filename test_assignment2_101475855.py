"""
Unit Tests for Assignment 2 — Port Scanner
"""

import unittest
from assignment2_101475855 import PortScanner, common_ports


class TestPortScanner(unittest.TestCase):

    def test_scanner_initialization(self):
        # just checking if the scanner initializes correctly
        scanner = PortScanner("127.0.0.1")

        # target should be set properly
        self.assertEqual(scanner.target, "127.0.0.1")

        # no scan results yet
        self.assertEqual(scanner.scan_results, [])

    def test_get_open_ports_filters_correctly(self):
        # simulate some scan results manually
        scanner = PortScanner("127.0.0.1")

        scanner.scan_results = [
            (22, "Open", "SSH"),
            (23, "Closed", "Telnet"),
            (80, "Open", "HTTP")
        ]

        # should only return the open ones
        open_ports = scanner.get_open_ports()

        self.assertEqual(len(open_ports), 2)

    def test_common_ports_dict(self):
        # just making sure important ports are mapped correctly
        self.assertEqual(common_ports[80], "HTTP")
        self.assertEqual(common_ports[22], "SSH")

    def test_invalid_target(self):
        # try setting an empty target (should not change)
        scanner = PortScanner("127.0.0.1")

        scanner.target = ""

        # target should still be the original one
        self.assertEqual(scanner.target, "127.0.0.1")


if __name__ == "__main__":
    unittest.main()