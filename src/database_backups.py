import os
import json
import subprocess
import smtplib
import glob

class DatabaseDump:
    """
    This class handles operations related to database dump,
    including creating a dump, compressing the dump, sending an email with the dump, and deleting the dump.
    """
    def __init__(self, config):
        self.host = config['host']
        self.database = config['database']
        self.user = config['user']
        self.password = config['password']
        self.mail_server = config['mail_server']
        self.email_recipient = config['email_recipient']
        self.dump_path = config['dump_path']
        self.messages = []

    def dump_db(self):
        # Build the command for dumping the database
        command = f"mysqldump -h {self.host} -u {self.user} -p{self.password} {self.database} > {self.dump_path}/{self.database}.sql"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # If the command was successful, log the success message
        # Otherwise, log the error message
        if result.returncode == 0:
            self.messages.append(f"Successfully dumped {self.database}")
        else:
            self.messages.append(f"Error dumping {self.database}: {result.stderr}")

    def compress_db_dump(self):
        command = f"gzip {self.dump_path}/{self.database}.sql"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            self.messages.append(f"Successfully compressed {self.database}")
        else:
            self.messages.append(f"Error compressing {self.database}: {result.stderr}")

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
        self.compress_db_dump()
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
    for db_config in config['databases']:
        db_dump = DatabaseDump(db_config)
        db_dump.process()

# This is the entry point of the script
if __name__ == '__main__':
    process_databases('config.json')
