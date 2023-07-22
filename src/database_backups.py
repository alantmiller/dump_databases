import os
import smtplib
import gzip
import shutil
import subprocess
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

class DatabaseDump:

    def __init__(self, db_dump_path, email):
        self.db_dump_path = db_dump_path
        self.email = email
        self.database = "my_database"
        self.user = "my_user"
        self.password = "my_password"

        # Configuring the logger
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            handlers=[
                                logging.FileHandler('db_dump.log'),
                                logging.StreamHandler()
                            ])

    def dump_db(self):
        """Perform the database dump"""
        try:
            command = f'mysqldump -u {self.user} -p{self.password} {self.database} > {self.db_dump_path}'
            subprocess.call(command, shell=True)
            logging.info("Database dumped successfully")
        except Exception as e:
            logging.error(f"An error occurred while dumping the database: {str(e)}")
