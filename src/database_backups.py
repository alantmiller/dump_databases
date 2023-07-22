
import os
import subprocess
import datetime
import tarfile
import smtplib
import json
import unittest
import logging
from email.message import EmailMessage
from concurrent.futures import ThreadPoolExecutor

class Database:
    def __init__(self, database, username, password):
        self.database = database.strip()
        self.username = username.strip()
        self.password = password.strip()


class DumpDatabases:
    def __init__(self):
        self.databases = []
        self.messages = []
        self.config = self.load_config()

        self.mysqldump_cmd = self.config['mysqldump_cmd']
        self.dump_dir = self.config['dump_dir']
        self.owner = self.config['owner']
        self.group = self.config['group']
        self.email_from = self.config['email_from']
        self.email_admin = self.config['email_admin']
        self.host = self.config['host']

        self.messages.append('STARTED @ {}'.format(datetime.datetime.now().strftime("%B %d, %Y, %I:%M%p")))

        # Additional configuration such as dump options and tar options can be added here.

    def load_config(self):
        # Load JSON configuration file
        with open('config.json') as json_file:
            data = json.load(json_file)
        return data

    def add_database(self, db):
        self.databases.append(db)
        self.messages.append('ADDED DATABASE: {}'.format(db.database))

    # The rest of the methods will follow the similar structure.

# The rest of the python code will be written here including error handling, testing and logging, etc.
