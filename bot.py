import os
import sys
import json
import time
import requests
from colorama import *

init(autoreset=True)

merah = Fore.LIGHTRED_EX
putih = Fore.LIGHTWHITE_EX
hijau = Fore.LIGHTGREEN_EX
kuning = Fore.LIGHTYELLOW_EX
biru = Fore.LIGHTBLUE_EX
reset = Style.RESET_ALL
bold = Style.BRIGHT

class CubeTod:
    def __init__(self):
        self.headers = {
            'content-length': '0',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; Redmi 4A / 5A Build/QQ3A.200805.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.185 Mobile Safari/537.36',
            'content-type': 'application/json',
            'accept': '*/*',
            'origin': 'https://www.thecubes.xyz',
            'x-requested-with': 'org.telegram.messenger',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.thecubes.xyz/',
            'accept-language': 'en,en-US;q=0.9',
        }
        self.boost_pool = False
        self.boost_amount = 0
        self.boost_interval_hours = 1  # Default boost interval in hours
        self.energy_threshold = 500  # Set the energy threshold
        self.interval = 5 * 60  # Reduced interval to 5 minutes
        self.sleep = 5  # Reduced sleep time between mining attempts to 5 seconds




    def main(self):
        banner = f"""
    
    {hijau}AUTO MINE {hijau}CUBE {putih}/ 
    
        """
        
        
        if len(sys.argv) <= 1:
            os.system('cls' if os.name == 'nt' else 'clear')
        print(banner)
        print('~' * 50)
        if not os.path.exists('data'):
            open('data', 'a')
        
        data = open('data', 'r').read().splitlines()
        
        if len(data) <= 0:
            self.log(f"{merah}data file is empty, please fill data file !")
            sys.exit()
            
        if not os.path.exists('user-agent'):
            open('user-agent', 'a')
        
        ua = open('user-agent', 'r').read().splitlines()
        if len(ua) <= 0:
            self.log(f"{merah}please fill user-agent file with your user-agent !")
            sys.exit()

        self.headers['user-agent'] = ua[0]

        total_accounts = len(data)
        self.log(f"{putih}Total accounts: {total_accounts}")

        self.boost_pool = input("Can you boost Pool? (y/n): ").lower() == 'y'
        if self.boost_pool:
            self.boost_amount = int(input("Boost amount: "))
            self.boost_interval_hours = int(input("Boost interval in hours: "))

        while True:
            print('~' * 50)
            for index, token_data in enumerate(data):
                token = self.login(token_data)
                while True:
                    res = self.mine(token)
                    if isinstance(res, str) and res == 'limit':
                        break
                    time.sleep(self.sleep)  # Reduced sleep time between mining attempts
                if self.boost_pool:
                    self.boost(token, self.boost_amount)
                self.claim_pool_balance(token)
                time.sleep(1)  # Wait 1 second before logging into the next account
            self.countdown(self.interval)

    def log(self, message):
        year, mon, day, hour, minute, second, a, b, c = time.localtime()
        mon = str(mon).zfill(2)
        hour = str(hour).zfill(2)
        minute = str(minute).zfill(2)
        second = str(second).zfill(2)
        print(f"{biru}[{year}-{mon}-{day} {hour}:{minute}:{second}] {message}")

    def countdown(self, t):
        while t:
            menit, detik = divmod(t, 60)
            jam, menit = divmod(menit, 60)
            jam = str(jam).zfill(2)
            menit = str(menit).zfill(2)
            detik = str(detik).zfill(2)
            print(f"waiting until {jam}:{menit}:{detik} ", flush=True, end="\r")
            t -= 1
            time.sleep(1)
        print("                          ", flush=True, end="\r")
    
    def mine(self, token):
        headers = self.headers
        data = {
            "token": token
        }
        headers['content-length'] = str(len(json.dumps(data)))
        res = self.http('https://server.questioncube.xyz/game/mined', headers, json.dumps(data))
        if res.status_code == 200:
            if '"mined_count"' in res.text:
                self.log(f"{bold}{hijau}Mined successfully{reset}")
                drop = res.json()['drops_amount']
                energy = res.json()['energy']
                mined = res.json()['mined_count']
                boxes = res.json()['boxes_amount']
                self.log(f"{bold}{kuning}Balance : {putih}{drop}{reset}")
                self.log(f"{bold}{hijau}Boxes amount : {putih}{boxes}{reset}")
                self.log(f"{bold}{kuning}Mined count : {putih}{mined}{reset}")
                self.log(f"{bold}{Fore.LIGHTMAGENTA_EX}Remaining Energy : {putih}{energy}{reset}")

                if int(energy) <= self.energy_threshold:
                    return 'limit'
                
                return True
        
        return False

    def login(self, data):
        url = "https://server.questioncube.xyz/auth"
        payload = {
            "initData": data
        }
        headers = self.headers
        headers['content-length'] = str(len(json.dumps(payload)))
        res = self.http(url, headers, json.dumps(payload))
        if res.status_code == 200:
            if '"token"' in res.text:
                token = res.json()['token']
                name = res.json()['username']
                energy = res.json()['energy']
                drop = res.json()['drops_amount']
                mined = res.json()['mined_count']
                self.log(f'{Style.BRIGHT}{Fore.LIGHTYELLOW_EX}-----------------------------{reset}')
                self.log(f"{bold}{Fore.CYAN}{name}{reset}")
                self.log(f'{bold}{kuning}Balance : {putih}{drop}{reset}')
                self.log(f'{bold}{hijau}Mined count : {putih}{mined}{reset}')
                self.log(f'{bold}{kuning}Energy : {putih}{energy}{reset}')
                return token
        
        self.log(f'{bold}{merah}failed to login, http status code : {kuning}{res.status_code}{reset}')
        sys.exit()

    def boost(self, token, amount):
        url = "https://server.questioncube.xyz/pools/boost"
        payload = {
            "amount": amount,
            "token": token
        }
        headers = self.headers
        headers['content-length'] = str(len(json.dumps(payload)))
        
        retry_attempts = 3  # Number of retry attempts
        retry_delay = 5  # Delay between retries in seconds
        
        for attempt in range(retry_attempts):
            res = self.http(url, headers, json.dumps(payload))
            if res.status_code == 200:
                self.log(f"{bold}{hijau}Pool boosted successfully{reset}")
                return True
            elif res.status_code == 400 and 'Not enough balance' in res.text:
                self.log(f"{bold}{merah}Not enough balance for boost pool: {kuning}{res.status_code}{reset}")
                return False
            elif res.status_code == 500:
                self.log(f"{bold}{merah}Failed to boost pool (attempt {attempt + 1}/{retry_attempts}), status code: {kuning}{res.status_code}{reset}")
                time.sleep(retry_delay)  # Wait before retrying
            else:
                self.log(f"{bold}{merah}Unexpected error while boosting pool, status code: {kuning}{res.status_code}{reset}")
                return False
        
        self.log(f"{bold}{merah}Failed to boost pool after {retry_attempts} attempts{reset}")
        return False

    def claim_pool_balance(self, token):
        url = "https://server.questioncube.xyz/pools/claim"
        payload = {
            "token": token
        }
        headers = self.headers
        headers['content-length'] = str(len(json.dumps(payload)))
        res = self.http(url, headers, json.dumps(payload))
        if res.status_code == 200:
            balance = res.json().get('balance', 0)
            if balance > 1:
                self.log(f"{bold}{hijau}Pool balance claimed successfully, balance: {putih}{balance}{reset}")
            else:
                self.log(f"{bold}{kuning}Pool balance is less than 1, not claimed{reset}")
                self.log(f'{Style.BRIGHT}{Fore.LIGHTYELLOW_EX}-----------------------------{reset}')
        else:
            self.log(f"{bold}{merah}Failed to claim pool balance, status code: {kuning}{res.status_code}{reset}")
                
    def http(self, url, headers, data=None):
        while True:
            try:
                if data is None:
                    res = requests.get(url, headers=headers)
                    return res

                res = requests.post(url, headers=headers, data=data)
                return res
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ReadTimeout,
                requests.exceptions.Timeout,
                requests.exceptions.HTTPError,
                requests.exceptions.RequestException,
                requests.exceptions.BaseHTTPError
            ):
                self.log(f"{merah}Failed to connect to the server, retrying in 5 seconds...{reset}")
                time.sleep(5)

if __name__ == "__main__":
    app = CubeTod()
    app.main()
