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
