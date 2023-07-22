import os
import json
import subprocess
import smtplib
import glob
from datetime import datetime
import requests


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

        self.ensure_directory_exists(self.dump_path)

    def ensure_directory_exists(self, directory):
        """
        Ensure that the specified directory exists.
        If it doesn't, attempt to create it.
        """
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                self.messages.append(f"Created directory {directory}")
            except Exception as e:
                self.messages.append(f"Error occurred while creating directory {directory}: {str(e)}")
                raise


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
            self.messages.append(f"Database {self.database} dumped successfully to {dump_file_path}")
            self.dump_file_path = dump_file_path
        except Exception as e:
            self.messages.append(f"Error occurred while dumping database {self.database}: {str(e)}")
            raise

    def manage_db_dumps(self):
        all_dumps = sorted(glob.glob(f"{self.dump_path}/{self.database}*"))
        while len(all_dumps) > 5:
            os.remove(all_dumps[0])
            all_dumps = all_dumps[1:]
            self.messages.append(f"Removed excess dump file for {self.database}")

    def process(self):
        self.dump_db()
        self.manage_db_dumps()
        return self.messages

def process_databases(config_file_path):
    """
    This function reads the JSON config file and processes each database.
    """
    # Load the config file
    with open(config_file_path) as f:
        config = json.load(f)

    all_messages = []
    # Loop over each database config and process the database
    for db_config in config['db']['databases']:
        db_dump = DatabaseBackup(db_config, config)
        messages = db_dump.process()
        all_messages.extend(messages)
        
    # After processing all databases, send a single email notification
    send_email_notification(config, all_messages)

def send_email_notification(config, messages):
    """
    This function sends an email with the summary of all databases using Mailgun's API.
    """
    # Construct the base URL for email API
    base_url = f"{config['email']['apiBaseUrl']}/{config['email']['domain']}"

    # Set the headers for email API authentication
    headers = {
        'Authorization': f'Bearer {config['email']['apiKey']}'
    }

    # Set the email data
    data = {
        'from': 'sender@example.com',
        'to': 'recipient@example.com', # replace with your recipient email
        'subject': 'DB Dump Report',
        'text': '\n'.join(messages),
    }

    # Send the email
    response = requests.post(base_url + '/messages', headers=headers, data=data)

    if response.status_code == 200:
        print(f"Email sent to {'recipient@example.com'}")
    else:
        print(f"Failed to send email: {response.content}")

# This is the entry point of the script
if __name__ == '__main__':
    process_databases('config.json')
