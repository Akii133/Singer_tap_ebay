# Singer_tap for ebay ledger api
This project provides a Singer Tap implementation for extracting financial transaction data from eBay's API using the Singer specification. It allows you to synchronize transaction data from eBay's financial API into compatible data destinations.

Installation
To install the tap, follow these steps:

Clone this repository: https://github.com/Akii133/Singer_tap_ebay/edit/main

git clone <repository_url>
cd ebay-ledger-tap

Install dependencies:
pip install -r requirements.txt

Configuration
Before running the tap, ensure you have configured the config.json file with your eBay API credentials and desired configuration parameters. Here's a sample config.json structure:

config. json
{
  "start_date": "2022-01-01T00:00:00Z",
  "access_token": "<your_ebay_access_token>",
  "username": "<your_ebay_username>",
  "password": "<your_ebay_password>"
}
Ensure the start_date is set in UTC format (YYYY-MM-DDTHH:MM
).

Usage
Running Discovery Mode
To discover available streams (data entities), run:
python3 run_tap.py --config config.json --discover > catalog.json

Synchronizing Data
To sync data from eBay's API using the configured parameters, run:

python3 run_tap.py --config config.json --catalog catalog.json --state state.json

Replace catalog.json and state.json with your desired file paths for catalog and state files.

