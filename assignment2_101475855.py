"""
Author: Kiana Sepasian
Assignment: #2
Description: Port Scanner — A tool that scans a target machine for open network ports
"""

# TODO: Import the required modules (Step ii)
# socket, threading, sqlite3, os, platform, datetime
import socket
import threading
import sqlite3
import os
import platform
import datetime


# TODO: Print Python version and OS name (Step iii)
print("Python Version:", platform.python_version())
print("Operating System:", os.name)


# Stores common port numbers and their service names
common_ports = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    8080: "HTTP-Alt"
}

# TODO: Create the NetworkTool parent class (Step v)
# - Constructor: takes target, stores as private self.__target
# - @property getter for target
# - @target.setter with empty string validation
# - Destructor: prints "NetworkTool instance destroyed"
class NetworkTool:
    def __init__(self, target):
        # save the target address (private so it can't be changed directly)
        self.__target = target

    # Q3: What is the benefit of using @property and @target.setter?
    # using property helps control how the value is accessed or changed.
    # instead of letting anything modify it directly, we can validate inputs.
    # here it prevents setting an empty target which could break the program.
    @property
    def target(self):
        return self.__target

    @target.setter
    def target(self, value):
        # make sure the target is not empty
        if value.strip() == "":
            print("Error: Target cannot be empty")
        else:
            self.__target = value

    def __del__(self):
        print("NetworkTool instance destroyed")




# Q1: How does PortScanner reuse code from NetworkTool?
# this class inherits from NetworkTool so it doesn't need to rewrite basic things like storing the target.
# for example, it uses the target from the parent class instead of defining it again.
# this makes the code cleaner and avoids repeating the same logic.

class PortScanner(NetworkTool):
    def __init__(self, target):
        super().__init__(target)
        self.scan_results = []
        self.lock = threading.Lock()

    def __del__(self):
        print("PortScanner instance destroyed")
        super().__del__()



    def scan_port(self, port):
        # Q4: What would happen without try-except here?
        # if we remove try-except, the program might crash when a port can't be reached.
        # since we are scanning many ports, errors are normal and should be handled.
        # this helps the program continue instead of stopping completely.

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)

            result = sock.connect_ex((self.target, port))

            if result == 0:
                status = "Open"
            else:
                status = "Closed"

            service_name = common_ports.get(port, "Unknown")

            self.lock.acquire()
            self.scan_results.append((port, status, service_name))
            self.lock.release()

        except socket.error as e:
            print(f"Error scanning port {port}: {e}")

        finally:
            sock.close()



    def get_open_ports(self):
        return [f for f in self.scan_results if f[1] == "Open"]
        

    # Q2: Why do we use threading instead of scanning one port at a time?
    # using threading makes the scan faster because multiple ports are checked at the same time.
    # if we scan one by one, it would take a long time especially for many ports.
    # this helps improve performance and makes the program more efficient.
    def scan_range(self, start_port, end_port):
        threads = []

        for port in range(start_port, end_port + 1):
            t = threading.Thread(target=self.scan_port, args=(port,))
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()







# TODO: Create save_results(target, results) function (Step vii)
# - Connect to scan_history.db
# - CREATE TABLE IF NOT EXISTS scans (id, target, port, status, service, scan_date)
# - INSERT each result with datetime.datetime.now()
# - Commit, close
# - Wrap in try-except for sqlite3.Error
def save_results(target, results):
    try:
        conn = sqlite3.connect("scan_history.db")
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target TEXT,
            port INTEGER,
            status TEXT,
            service TEXT,
            scan_date TEXT
        )
        """)

        for port, status, service in results:
            cursor.execute(
                "INSERT INTO scans (target, port, status, service, scan_date) VALUES (?, ?, ?, ?, ?)",
                (target, port, status, service, str(datetime.datetime.now()))
            )

        conn.commit()
        conn.close()

    except sqlite3.Error as e:
        print(f"Database error: {e}")


# TODO: Create load_past_scans() function (Step viii)
# - Connect to scan_history.db
# - SELECT all from scans
# - Print each row in readable format
# - Handle missing table/db: print "No past scans found."
# - Close connection
def load_past_scans():
    try:
        conn = sqlite3.connect("scan_history.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM scans")
        rows = cursor.fetchall()

        for row in rows:
            print(f"[{row[5]}] {row[1]} : Port {row[2]} ({row[4]}) - {row[3]}")

        conn.close()

    except sqlite3.Error:
        print("No past scans found.")


# ============================================================
# MAIN PROGRAM
# ============================================================
if __name__ == "__main__":
    try:
        # get target IP from user (if nothing entered, use localhost)
        target = input("Enter target IP (default 127.0.0.1): ").strip()
        if target == "":
            target = "127.0.0.1"

        # ask for port range
        start_port = int(input("Enter start port (1-1024): "))
        end_port = int(input("Enter end port (1-1024): "))

        # basic validation so user doesn't enter weird values
        if start_port < 1 or end_port > 1024:
            print("Port must be between 1 and 1024.")
            exit()

        # make sure range makes sense
        if end_port < start_port:
            print("End port must be greater than or equal to start port.")
            exit()

    except ValueError:
        # handles when user types something that's not a number
        print("Invalid input. Please enter a valid integer.")
        exit()

    # create scanner object with the given target
    scanner = PortScanner(target)

    print(f"\nScanning {target} from port {start_port} to {end_port}...\n")

    # start scanning the range
    scanner.scan_range(start_port, end_port)

    # get only open ports
    open_ports = scanner.get_open_ports()

    print(f"\n--- Scan Results for {target} ---")

    # print results in a readable way
    for port, status, service in open_ports:
        print(f"Port {port}: {status} ({service})")

    print("------")
    print(f"Total open ports found: {len(open_ports)}")

    # save everything (not just open ones) to database
    save_results(target, scanner.scan_results)

    # ask user if they want to see previous scans
    choice = input("Would you like to see past scan history? (yes/no): ").lower()

    if choice == "yes":
        load_past_scans()


# Q5: New Feature Proposal
# one feature I would add is a basic security check for open ports.
# for example, if port 80 is open, the program can warn that HTTP is not secure.
# this can be done using a simple if-statement to check known ports and print warnings.

# Diagram: See diagram_101475855.png in the repository root