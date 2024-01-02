# Monthly Printer Report (for Brother Printers)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/flo602/Monthly-Printer-Report/blob/main/LICENSE)

This automated script is designed to work with Brother printers. It automates the collection of printer data and generates a monthly report. It checks the status of Brother printers, downloads CSV files, and sends a structured report via email.

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Features

- Checks the status and availability of Brother printers.
- Downloads CSV data files from networked Brother printers.
- Generates a structured report with specified columns.
- Sends the report via email.

## Getting Started

### Prerequisites

- Python 3.x installed on your system.
- Required Python libraries installed (requests, pandas, yaml, smtplib, etc.).

### Installation

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/yourusername/Monthly-Printer-Report.git

2. Install the required Python libraries using pip:

    ```bash
    pip install -r requirements.txt

## USAGE 

1. Configure the config.yml file with your specific settings:

   ```yaml
   printer_ips:
  - 192.168.1.100
  - 192.168.1.101
  # Add more printer IPs as needed

printer_users:
  192.168.1.100: UserA
  192.168.1.101: UserB
  # Assign user names to printer IPs

required_columns:
  - Date
  - PageCount
  - Status
  # Define required columns in the report

smtp_info:
  from_address: your_email@example.com
  to_addresses:
    - recipient1@example.com
    - recipient2@example.com
  host: smtp.example.com
  port: 587
  user: your_email@example.com
  password: your_email_password
  # SMTP email configuration

report_schedule:
  day_of_month: 20
  hour: 23
  minute: 59
  # Schedule for report generation

2. Run the script using the following command:

   ```bash
   python printer_report.py

You can use the -f option to force report generation and sending, and the -D option to enable debug mode.

3. The script will check Brother printer status, download CSV files, generate a report, and send it via email.
## Configuration

Edit the config.yml file with your specific configurations.

## Contributing

Contributions are welcome! Please create a pull request with any improvements or bug fixes.

## License

This project is licensed under the MIT License.
