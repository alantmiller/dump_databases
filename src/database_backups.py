import os
import json
import subprocess
import smtplib
import glob
from datetime import datetime

class DatabaseBackup:
    
    def __init__(self, db_config, global_config):
        """
        Initialize with the host, database name, username, password, mail server, recipient email, dump path and dump options
        """
        self.host = global_config["db"]["host"]
        self.database = db_config["name"]
        self.user = db_config["user"]
        self.password = db_config["password"]
        self.email_config = global_config["email"]
        self.dump_path = global_config["dump_path"]
        self.dump_options = global_config["dump_options"] 

        self.messages = []


    def dump_db(self):
        """
        This function dumps the database into a gzip compressed file.
        """
        try:
            # Here we're adding time to the file name using strftime's %H%M%S for HourMinuteSecond
            dump_file_path = os.path.join(self.dump_path, f"{self.database}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql.gz")
            with open(dump_file_path, "wb") as dump_file:
                # Execute the mysqldump command, pipe it to gzip and write the output to a file
                mysqldump_command = ['mysqldump', '-h', self.host, '-u', self.user, '-p' + self.password, '--databases', self.database] + self.dump_options
                gzip_command = ['gzip']
                mysqldump_process = subprocess.Popen(mysqldump_command, stdout=subprocess.PIPE)
                gzip_process = subprocess.Popen(gzip_command, stdin=mysqldump_process.stdout, stdout=dump_file)
                mysqldump_process.stdout.close()  # Allow mysqldump_process to receive a SIGPIPE if gzip_process exits
                gzip_process.communicate()  # Blocks until process completes
            self.message_logger.log_info(f"Database {self.database} dumped successfully to {dump_file_path}")
            self.dump_file_path = dump_file_path
        except Exception as e:
            self.message_logger.log_error(f"Error occurred while dumping database {self.database}: {str(e)}")
            raise

    def email_db_dump(self):
        email_body = '\n'.join(self.messages)
        message = f"Subject: DB Dump Report\n\n{email_body}"

        server = smtplib.SMTP(self.mail_server)
        server.sendmail('sender@example.com', self.email_recipient, message)
        server.quit()

        self.messages.append(f"Email sent to {self.email_recipient}")

    def manage_db_dumps(self):
        all_dumps = sorted(glob.glob(f"{self.dump_path}/{self.database}*"))
        while len(all_dumps) > 5:
            os.remove(all_dumps[0])
            all_dumps = all_dumps[1:]
            self.messages.append(f"Removed excess dump file for {self.database}")

    def process(self):
        self.dump_db()
        self.email_db_dump()
        self.manage_db_dumps()


def process_databases(config_file_path):
    """
    This function reads the JSON config file and processes each database.
    """
    # Load the config file
    with open(config_file_path) as f:
        config = json.load(f)

    # Loop over each database config and process the database
    for db_config in config['db']['databases']:
        db_dump = DatabaseBackup(db_config, config)
        db_dump.process()

# This is the entry point of the script
if __name__ == '__main__':
    process_databases('config.json')
