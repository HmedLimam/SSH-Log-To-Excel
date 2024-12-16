"""
    ssh_log_to_excel.py

    Transforms SSH log files into an Excel spreadsheet.
    Geolocates IP addresses, providing country and city.

    Created by ahmed.ovh.

    Full story can be read here
    https://book.ahmed.ovh/information-security/hard-learned-security-lessons/the-dangers-of-default-ssh-configurations
"""

import geocoder
import pycountry
import pandas as pd
from itertools import islice
import pickle
from colorama import Fore, Style, init as init_colorama
import argparse
import os
import re

init_colorama()
parser = argparse.ArgumentParser(
    description="Parse SSH log attempts and save them to an Excel file."
)

parser.add_argument('-i', "--input", help="Specify the text file containing SSH attempts.", required=True)
parser.add_argument('-o', "--output", help="Specify the file name where the split data will be saved in table format.", required=True)

args = parser.parse_args()

if not os.path.isfile(args.input):
    print(f"Error: The input file '{args.input}' does not exist in the current directory.")
    exit(1)

input_file = args.input
output_file = args.output

print(Fore.LIGHTGREEN_EX, f"[+] Input file: {input_file}", Style.RESET_ALL)

data = []
old_last_reached_attempt = last_reached_attempt = 0

try:
    with open("cached_ips.pkl", "rb") as file:
        cached_ips = pickle.load(file)
except FileNotFoundError:
    cached_ips = []

with open(input_file) as file:
    number_of_lines = len(file.readlines())
    print(Fore.LIGHTYELLOW_EX, f"[!] Number of lines: {number_of_lines}", Style.RESET_ALL)
    file.seek(0)
    for _, line in enumerate(islice(file, last_reached_attempt, None)):
        line_processed_successfully = False
        while not line_processed_successfully:
            print(f"Current Line: {_+1 + old_last_reached_attempt} - Current Progress: {((_+1 + old_last_reached_attempt) / number_of_lines) * 100:.2f}%", end='\r', flush=True)
            hostname = line.split(" ")[3]
            dateAndTime = line.split(f" {hostname}")[0]
            result = re.search(r"sshd\[\d+\]: (\w+)", line).group(1)
            authType = line.split(f"{result} ")[1].split(" ")[0]
            username = line.split("for ")[1]
            if "invalid user" in username:
                username = line.split("for invalid user ")[1]
            username = username.split(" ")[0]
            attackerIp = line.split("from ")[1].split(" ")[0]

            try:
                attacker_info = next((entry for entry in cached_ips if entry["ip"] == attackerIp), None)
                if attacker_info:
                    attackerCountry = attacker_info["country"]
                    attackerCity = attacker_info["city"]
                else:
                    attackerGeolocation = geocoder.ip(attackerIp)
                    attackerCountry = pycountry.countries.get(alpha_2=attackerGeolocation.country).name
                    attackerCity = attackerGeolocation.city
                    cached_ips.append({"ip": attackerIp, "country": attackerCountry, "city": attackerCity})

                data.append({
                    'dateAndTime': dateAndTime,
                    'result': result,
                    'authType': authType,
                    'username': username,
                    'attackerIp': attackerIp,
                    'attackerCountry': attackerCountry,
                    'attackerCity': attackerCity,
                })
                last_reached_attempt = _+1+old_last_reached_attempt
                line_processed_successfully = True
            except:
                if last_reached_attempt != number_of_lines:
                    df = pd.DataFrame(data)
                    df.to_excel(f'{output_file}_{last_reached_attempt}.xlsx', index=True)

                    with open("cached_ips.pkl", "wb") as cached_ips_file:
                        pickle.dump(cached_ips, cached_ips_file)

                    print(Fore.LIGHTBLUE_EX,
                        f"Rate limit reached: {_ + 1 + old_last_reached_attempt} - Current Progress: {((_ + 1 + old_last_reached_attempt) / number_of_lines) * 100:.2f}%", Style.RESET_ALL)
                    print(Fore.LIGHTGREEN_EX, f"[+] Output file: {output_file}_{last_reached_attempt}.xlsx.", Style.RESET_ALL)
                    print(Fore.YELLOW, "[/] Change your VPN Server and hit any key to continue.", Style.RESET_ALL)
                    input()
                    #TODO: Add an automatic check for public ip change
                    print(Fore.LIGHTGREEN_EX, "[+] Continuing..", Style.RESET_ALL)
                    data = []

    df = pd.DataFrame(data)
    df.to_excel(f'{output_file}_{last_reached_attempt}.xlsx', index=True)

    with open("cached_ips.pkl", "wb") as cached_ips_file:
        pickle.dump(cached_ips, cached_ips_file)

    print(flush=True)
    print(Fore.LIGHTGREEN_EX, f"[+] Done processing {number_of_lines} lines.", Style.RESET_ALL)
    print(Fore.LIGHTYELLOW_EX, "[/] Creating final output file..", Style.RESET_ALL)

    # Get the list of all newly created Excel files in the current directory
    xlsx_files = [file for file in os.listdir() if file.endswith('.xlsx') and file.startswith(output_file)]

    if len(xlsx_files) == 1:
        os.rename(xlsx_files[0], f"{output_file}.xlsx")
    else:
        xlsx_files.sort(key=lambda x: int(re.search(r'(\d+)', x).group()))

        dfs = []

        for file in xlsx_files:
            df = pd.read_excel(file)
            # Remove the first column (index column)
            df = df.iloc[:, 1:]
            dfs.append(df)

        merged_df = pd.concat(dfs, ignore_index=True)
        merged_df.to_excel(f'{output_file}.xlsx', index=False)

        # Delete the temporary files
        for file in xlsx_files:
            try:
                os.remove(file)
            except Exception as e:
                print(f"Failed to delete {file}: {e}")

    print(Fore.LIGHTGREEN_EX, f"[+] Output file: {output_file}.xlsx.", Style.RESET_ALL)