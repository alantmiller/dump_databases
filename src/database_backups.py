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
        self.log_messages = []
        self.database = "my_database"
        self.user = "my_user"
        self.password = "my_password"

    def write_msg(self, msg):
        """Add a message to the log_messages list and print it"""
        self.log_messages.append(msg)
        print(msg)

    def dump_db(self):
        """Perform the database dump"""
        try:
            command = f'mysqldump -u {self.user} -p{self.password} {self.database} > {self.db_dump_path}'
            subprocess.call(command, shell=True)
            self.write_msg("Database dumped successfully")
        except Exception as e:
            self.write_msg(f"An error occurred while dumping the database: {str(e)}")


    def compress_db_dump(self):
        """Compress the database dump"""
        try:
            with open(self.db_dump_path, 'rb') as f_in:
                with gzip.open(self.db_dump_path + '.gz', 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            self.write_msg("Database dump compressed successfully")
        except Exception as e:
            self.write_msg(f"An error occurred while compressing the database dump: {str(e)}")

    def write_log(self):
        """Write the log messages to a file"""
        try:
            logging.basicConfig(filename='db_dump.log', level=logging.INFO)
            for msg in self.log_messages:
                logging.info(msg)
            self.write_msg("Log written successfully")
        except Exception as e:
            self.write_msg(f"An error occurred while writing the log: {str(e)}")

    def send_email(self):
        """Send an email with the log messages"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = self.email
            msg['Subject'] = "Database Dump Log"
            body = "\n".join(self.log_messages)
            msg.attach(MIMEText(body, 'plain'))
            server = smtplib.SMTP('localhost')
            text = msg.as_string()
            server.sendmail(self.email, self.email, text)
            server.quit()
            self.write_msg("Email sent successfully")
        except Exception as e:
            self.write_msg(f"An error occurred while sending the email: {str(e)}")

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

# create an instance of the class
db_dump = DatabaseDump(db_dump_path="/path/to/db_dump", email="user@example.com")

# start the process
db_dump.run()
