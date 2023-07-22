import os
import smtplib
import gzip
import shutil
import subprocess
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

class DatabaseDump:

    def __init__(self, host, database, user, password, mail_server, email_recipient, dump_path):
        self.dump_path = dump_path
        current_date = datetime.now().strftime('%Y_%m_%d')
        self.db_dump_path = f"{self.dump_path}/db_dump_{self.database}_{current_date}.sql"
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

    def compress_db_dump(self):
        """Compress the dumped database"""
        try:
            with open(self.db_dump_path, 'rb') as f_in:
                with gzip.open(self.db_dump_path + '.gz', 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            logging.info("Database dump compressed successfully")
        except Exception as e:
            logging.error(f"An error occurred while compressing the database dump: {str(e)}")

    def email_db_dump(self):
        """Email the compressed database dump"""
        try:
            msg = MIMEMultipart()
            msg['From'] = 'my_email@example.com'
            msg['To'] = self.email
            msg['Subject'] = 'Database Dump'

            text = MIMEText('Please find attached the latest database dump.')
            msg.attach(text)

            # Connect to the mail server
            server = smtplib.SMTP('my_smtp_server.com', 587)
            server.starttls()

            # Login Credentials for sending the mail
            password = "my_email_password"
            server.login(msg['From'], password)

            # Send the message
            text = msg.as_string()
            server.sendmail(msg['From'], msg['To'], text)
            server.quit()

            logging.info("Database dump emailed successfully")
        except Exception as e:
            logging.error(f"An error occurred while emailing the database dump: {str(e)}")

    def delete_db_dump(self):
        """Delete the local database dump"""
        try:
            os.remove(self.db_dump_path)
            logging.info("Database dump deleted successfully")
        except Exception as e:
            logging.error(f"An error occurred while deleting the database dump: {str(e)}")

    def cleanup_old_dumps(self):
        # Get the list of all dump files for the database
        dump_files = glob.glob(f"{self.dump_path}/db_dump_{self.database}_*.sql")

        # Sort the files by creation date
        dump_files.sort(key=os.path.getctime)

        # If more than 5 files, delete the oldest ones
        while len(dump_files) > 5:
            os.remove(dump_files[0])
            del dump_files[0]


if __name__ == '__main__':
    db_dump = DatabaseDump('/path/to/your/db_dump.sql', 'your_email@example.com')
    db_dump.dump_db()
    db_dump.compress_db_dump()
    db_dump.email_db_dump()
    db_dump.delete_db_dump()
