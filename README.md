# SSH Log to Excel and IP Geolocation

## Overview  
This tool processes SSH log files and converts them into an **Excel spreadsheet**. It also geolocates IP addresses to provide **country** and **city** information, making it easier to analyze and report on SSH activity.  

The Excel output was designed to seamlessly integrate with **Power BI dashboards** for improved **data analysis** and **reporting**.

## Features  
- Converts SSH logs into structured Excel spreadsheets.  
- Geolocates IP addresses, providing **country** and **city** details.  
- **Waits for the user to change VPN servers** when rate-limiting occurs for the geolocation service, ensuring smooth processing of IP addresses.
- Saves already resolved IP addresses as a caching mechanism and make the process faster/

## Requirements  
- Python 3.x  
- Required libraries `pip install -r requirements.txt`

## Usage
1. Run the script `python ssh_log_to_excel.py -i log_file.txt -o output`
2. If the geolocation service enforces rate-limiting, the script will pause and prompt the user to switch VPS servers. After switching, continue execution to geolocate the remaining IP addresses.
3. The output Excel file `output.xlsx` will be generated in the current directory.

## Example Output
| dateAndTime       | PasswordAuthOrNoneAuth     | username       | attackerIp          |  attackerCountry | attackerCity |
|------------|----------------|---------------|---------------|----|----| 
| Aug 20 20:15:56 | password    | root | 165.22.4.32 | United States |   North Bergen | 
