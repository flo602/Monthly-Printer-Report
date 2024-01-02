# Import necessary libraries
import requests
import pandas as pd
from datetime import datetime
import yaml
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import subprocess
import calendar
import argparse
import schedule
import time
import logging

# Set the path for the log file
log_file_path = r"C:\recupimpression\log.txt"

# Configure logging settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler(log_file_path), logging.StreamHandler()])

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--force", help="Force report generation and sending", action="store_true")
parser.add_argument("-D", "--debug", help="Enable debug mode", action="store_true")
args = parser.parse_args()

# Enable debug mode if specified
if args.debug:
    logging.getLogger().setLevel(logging.DEBUG)

# Read configurations from a YAML file
try:
    with open(r"C:\recupimpression\config.yml", 'r') as file:
        config = yaml.safe_load(file)
except Exception as e:
    logging.error(f"Error reading the configuration file: {e}")
    exit(1)

# Extract configurations
try:
    printer_ips = config['printer_ips']
    printer_users = config['printer_users']
    required_columns = config['required_columns']
    smtp_info = {
        'from_address': config['smtp_info']['from_address'],
        'to_addresses': config['smtp_info']['to_addresses'],
        'host': config['smtp_info']['host'],
        'port': config['smtp_info']['port'],
        'user': config['smtp_info']['user'],
        'password': config['smtp_info']['password']
    }
except KeyError as e:
    logging.error(f"Missing configuration: {e}")
    exit(1)

# Other configurations
current_month = datetime.now().strftime("%m")
current_year = datetime.now().strftime("%Y")
non_structured_folder = f"C:\\recupimpression\\data_non_structurer\\{current_month}_{current_year}"
structured_folder = "C:\\recupimpression\\data_structurer"
os.makedirs(non_structured_folder, exist_ok=True)
os.makedirs(structured_folder, exist_ok=True)

# Function to download and save CSV files
def download_and_save_csv(ip, folder):
    try:
        url = f"http://{ip}/etc/mnt_info.csv"
        response = requests.get(url)
        if response.status_code == 200:
            date_str = datetime.now().strftime("%d_%m_%Y")
            file_name = f"{folder}/{ip}_{date_str}_non_structurer.csv"
            with open(file_name, 'wb') as file:
                file.write(response.content)
            return file_name
        else:
            logging.error(f"HTTP request failed for IP {ip} with status code: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Error during CSV download and save for IP {ip}: {e}")
        return None

# Function to check if printers are online
def is_printer_up(ip):
    try:
        response = subprocess.run(['ping', '-c', '1', ip], stdout=subprocess.PIPE)
        result = response.returncode == 0
        if result:
            logging.info(f"Printer {ip} is online.")
        else:
            logging.warning(f"Printer {ip} is not online.")
        return result
    except Exception as e:
        logging.error(f"Error checking printer {ip}: {e}")
        return False

# Function to generate and send the report
def generate_and_send_report():
    try:
        dataframes = []
        for ip in printer_ips:
            file_name = download_and_save_csv(ip, non_structured_folder)
            if file_name:
                try:
                    df = pd.read_csv(file_name, encoding='utf-8')
                except UnicodeDecodeError:
                    df = pd.read_csv(file_name, encoding='latin1')
                df['IP Address'] = ip
                df['Printer User'] = printer_users.get(ip, 'Unknown')
                dataframes.append(df)

        structured_report = pd.concat(dataframes, ignore_index=True)
        final_columns = ['Printer User'] + required_columns
        structured_report = structured_report[final_columns]

        file_path = f"{structured_folder}/report_{current_month}_{current_year}_structured.csv"
        structured_report.to_csv(file_path, index=False)

        send_email(file_path, smtp_info)
    except Exception as e:
        logging.error(f"Error generating and sending the report: {e}")

# Function to send the file via email
def send_email(file_path, smtp_info):
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_info['from_address']
        msg['To'] = ", ".join(smtp_info['to_addresses'])
        msg['Subject'] = "Monthly Printer Report"

        body = "Please find attached the monthly printer report."
        msg.attach(MIMEText(body, 'plain'))

        attachment = open(file_path, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(file_path)}")

        msg.attach(part)
        server = smtplib.SMTP(smtp_info['host'], smtp_info['port'])
        server.starttls()
        server.login(smtp_info['user'], smtp_info['password'])
        text = msg.as_string()
        server.sendmail(smtp_info['from_address'], smtp_info['to_addresses'], text)
        server.quit()
    except Exception as e:
        logging.error(f"Error sending email: {e}")

# Function to check all printers and generate/send the report
def check_printers_and_send_report(force=False):
    try:
        today = datetime.now()
        last_day_of_month = calendar.monthrange(today.year, today.month)[1]
        is_last_day_of_month = today.day == last_day_of_month

        # Check if all printers are online
        all_printers_up = all(is_printer_up(ip) for ip in printer_ips)
        
        if all_printers_up or force:
            generate_and_send_report()
            return True
        else:
            logging.info("Not all printers are online.")
            return False
    except Exception as e:
        logging.error(f"Error checking printers and sending the report: {e}")
        return False

# Schedule to check printer status daily at 12:00 PM
schedule.every().day.at("12:00").do(lambda: check_printers_and_send_report())

# Schedule to generate and send the report on the last day of the month
report_schedule = config.get('report_schedule', {})
day_of_month = report_schedule.get('day_of_month')
hour = report_schedule.get('hour')
minute = report_schedule.get('minute')

schedule.every().day.at(f"{hour}:{minute}").do(lambda: check_printers_and_send_report(True) if datetime.now().day == day_of_month else None)

# Check for the -f argument
if args.force:
    logging.info("Option -f enabled, forcing report generation.")
    result = check_printers_and_send_report(True)
    if result:
        logging.info("Report sent. Exiting the script.")
        exit(0)
    else:
        logging.error("Failed to send the report.")
        exit(1)

# Main loop for the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)
