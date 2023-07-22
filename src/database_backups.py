import os
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import subprocess
import shlex

class DatabaseDump:

    def __init__(self, config_file):
        """Initialize the class with configuration settings"""
        # Read the configuration file
        with open(config_file, "r") as file:
            self.config = json.load(file)
        
        # Setup variables based on configuration
        self.db_host = self.config["database"]["host"]
        self.db_user = self.config["database"]["user"]
        self.db_password = self.config["database"]["password"]
        self.db_name = self.config["database"]["name"]
        self.db_dump_path = self.config["paths"]["db_dump_path"]
        self.log_path = self.config["paths"]["log_path"]
        self.email_admin = self.config["email"]["admin"]
        self.email_subject = self.config["email"]["subject"]
        self.email_from = self.config["email"]["from"]
        self.msgs = []


    def run(self):
        """Run the database dump process"""
        try:
            self.write_msg("Starting database dump process...")
            self.dump_db()
            self.compress_db_dump()
            self.write_msg("Database dump process completed successfully!")
        except Exception as e:
            self.write_msg(f"An error occurred: {str(e)}")
        finally:
            self.write_log()
            self.send_email()
            

    def log(self, msg):
        """Log a message to the list of messages"""
        self.msgs.append(msg)

    def dump_database(self):
        """Dump the database to a file"""
        dump_file = os.path.join(self.db_dump_path, f"{self.db_name}.sql")
        dump_command = f"mysqldump -h {self.db_host} -u {self.db_user} -p{self.db_password} {self.db_name} > {dump_file}"

        # Use a subprocess to run the dump command
        process = subprocess.run(shlex.split(dump_command), shell=False)
        
        if process.returncode == 0:
            self.log(f"Database dumped to {dump_file}")
        else:
            self.log("Database dump failed")

    def write_log(self):
        """Write log messages to a file"""
        log_file = os.path.join(self.db_dump_path, "db_dump.log")
        with open(log_file, 'w') as file:
            for msg in self.msgs:
                file.write(f"{msg}\n")

    def send_email(self):
        """Send an email with the log file"""
        print(f"Sending an email with the log file {os.path.join(self.db_dump_path, 'db_dump.log')} to {self.email}")



# create an instance of the class
db_dump = DatabaseDump(db_dump_path="/path/to/db_dump", email="user@example.com")

# start the process
db_dump.run()

