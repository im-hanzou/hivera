import requests
import time
from datetime import datetime, timezone
import json
from colorama import Fore, Style, init
import signal
import sys
import urllib.parse

init(autoreset=True)

contribute_url = "https://api.hivera.org/v2/engine/contribute"
powers_url = "https://api.hivera.org/users/powers"
auth_url = "https://api.hivera.org/auth"
metric_self_url = "https://api.hivera.org/metric/self"
referal_auth = "https://api.hivera.org/referral?referral_code=90820c338&"  

def exit_handler(sig, frame):
    print(f"\n{Fore.RED+Style.BRIGHT}Bot stopped !{Style.RESET_ALL}")
    sys.exit(0)

signal.signal(signal.SIGINT, exit_handler)

auth_data_file = "data.txt"
auth_data_list = []

def parse_auth_data(raw_auth_data):
    parsed_data = urllib.parse.parse_qs(raw_auth_data, strict_parsing=True)
    auth_data = {k: v[0] for k, v in parsed_data.items()}
    if 'user' in auth_data:
        try:
            user_json = urllib.parse.unquote(auth_data['user'])
            auth_data['user'] = json.loads(user_json)
        except json.JSONDecodeError as e:
            auth_data['user'] = {}
        except Exception as e:
            auth_data['user'] = {}
    return auth_data

def is_valid_auth_data(auth_data):
    required_fields = ['user', 'chat_instance', 'chat_type', 'auth_date', 'signature', 'hash']
    return all(field in auth_data for field in required_fields)

try:
    with open(auth_data_file, "r") as file:
        for line_number, line in enumerate(file, 1):
            line = line.strip()
            if line:
                parsed_auth = parse_auth_data(line)
                if is_valid_auth_data(parsed_auth):
                    auth_data_list.append({'parsed': parsed_auth, 'raw': line})
                else:
                    print(f"{Fore.RED}Invalid auth_data structure at line {line_number}: {line}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Loaded {len(auth_data_list)}  accounts.{Style.RESET_ALL}")
except FileNotFoundError:
    print(f"{Fore.RED}Error: The file {auth_data_file} was not found.{Style.RESET_ALL}")

proxies = []
use_proxy = False
min_power = 500

if use_proxy:
    try:
        with open("proxy.txt", "r") as proxy_file:
            proxies = [line.strip() for line in proxy_file.readlines() if line.strip()]
        if proxies:
            print(f"{Fore.GREEN}Loaded {len(proxies)} proxies.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Proxy file is empty. Proceeding without proxies.{Style.RESET_ALL}")
            use_proxy = False
    except FileNotFoundError:
        print(f"{Fore.RED}Proxy file not found. Proceeding without proxies.{Style.RESET_ALL}")
        use_proxy = False

def get_username(raw_auth_data):
    try:
        response = requests.get(
            f"{auth_url}",
            params={"auth_data": raw_auth_data},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            result = response.json().get("result", {})
            username = result.get("username", "Unknown")
            return username
        else:
            print(f"{Fore.RED}Error fetching username. Status Code: {response.status_code}{Style.RESET_ALL}")
          
            return "Unknown"
    except Exception as e:
   
        return "Unknown"
def get_activity(raw_auth_data, proxy=None):
    """
    Fetches the rank and earned metrics for the user.
    """
    try:
        params = {"auth_data": raw_auth_data}
        headers = {"Content-Type": "application/json"}

        if proxy:
            response = requests.get(
                referal_auth,
                params=params,
                headers=headers,
                proxies={"http": proxy, "https": proxy},
                timeout=10
            )
        else:
            response = requests.get(
                referal_auth,
                params=params,
                headers=headers,
                timeout=10
            )

        if response.status_code == 200:
            
            return True
        else:
           
            return False
    except Exception as e:
      
        return False
    
def get_metrics(raw_auth_data, proxy=None):
    try:
        params = {"auth_data": raw_auth_data}
        headers = {"Content-Type": "application/json"}

        if proxy:
            response = requests.get(
                metric_self_url,
                params=params,
                headers=headers,
                proxies={"http": proxy, "https": proxy},
                timeout=10
            )
        else:
            response = requests.get(
                metric_self_url,
                params=params,
                headers=headers,
                timeout=10
            )

        if response.status_code == 200:
            data = response.json().get("result", {})
            rank = data.get("rank", "N/A")
            earned = data.get("earned", "N/A")
            return rank, earned
        else:
         
            return "N/A", "N/A"
    except Exception as e:
    
        return "N/A", "N/A"

def check_power(raw_auth_data, proxy=None):
    try:
        params = {"auth_data": raw_auth_data}
        headers = {"Content-Type": "application/json"}

        if proxy:
            response = requests.get(
                f"{powers_url}",
                params=params,
                headers=headers,
                proxies={"http": proxy, "https": proxy},
                timeout=10
            )
        else:
            response = requests.get(
                f"{powers_url}",
                params=params,
                headers=headers,
                timeout=10
            )

        if response.status_code == 200:
            power_data = response.json().get("result", {})
            current_power = power_data.get("POWER", 0)
            power_capacity = power_data.get("POWER_CAPACITY", 0)
            hivera = power_data.get("HIVERA", 0)

       
            return True, current_power, power_capacity
            
        else:
            
            return False, 0, 0
    except Exception as e:
 
        return False, 0, 0

def post_request(raw_auth_data, proxy=None):
    from_date = int(datetime.now(timezone.utc).timestamp() * 1000)
    payload = {
        "from_date": from_date,
        "quality_connection": 100,
        "times": 100
    }

    try:
        params = {"auth_data": raw_auth_data}
        headers = {"Content-Type": "application/json"}

        if proxy:
            response = requests.post(
                f"{contribute_url}",
                params=params,
                json=payload,
                headers=headers,
                proxies={"http": proxy, "https": proxy},
                timeout=10
            )
        else:
            response = requests.post(
                f"{contribute_url}",
                params=params,
                json=payload,
                headers=headers,
                timeout=10
            )

        if response.status_code == 200:
            return True, response.json()
        else:
           
            return False, response.text
    except Exception as e:
     
        return False, "Error occurred"

def print_header(title):
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}{title}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'-' * (len(title) + 2)}{Style.RESET_ALL}")

def animated_loading(duration):
    frames = ["|", "/", "-", "\\"]
    end_time = time.time() + duration
    while time.time() < end_time:
        remaining_time = int(end_time - time.time())
        for frame in frames:
            print(f"\rMenunggu waktu claim berikutnya {frame} - Tersisa {remaining_time} detik         ", end="", flush=True)
            time.sleep(0.25)
    print("\rMenunggu waktu claim berikutnya selesai.                            ", flush=True)
 

def print_welcome_message():
    print(Fore.WHITE + r"""
          
█▀▀ █░█ ▄▀█ █░░ █ █▄▄ █ █▀▀
█▄█ █▀█ █▀█ █▄▄ █ █▄█ █ ██▄
          """)
    print(Fore.GREEN + Style.BRIGHT + "Hivera Miner")
    print(Fore.YELLOW + Style.BRIGHT + "Free Konsultasi Join Telegram Channel: https://t.me/gsc_lobby")
  

if __name__ == "__main__":
    if not auth_data_list:
        print(f"{Fore.RED} Auth data kosong.{Style.RESET_ALL}")
        sys.exit(1)
    proxy_index = 0
    while True:
 
        for auth_entry in auth_data_list:
            parsed_auth = auth_entry['parsed']
            raw_auth = auth_entry['raw']
            username = parsed_auth.get('user', {}).get('username', 'No Username')
            print(f"\n{Fore.CYAN}[ Username ] : {username}{Style.RESET_ALL}")
            
            proxy = None
            if use_proxy and proxies:
                proxy = proxies[proxy_index % len(proxies)]
                print(f"{Fore.YELLOW}[ Proxy ] : {proxy}{Style.RESET_ALL}")
            elif use_proxy:
                print(f"{Fore.YELLOW}[ Proxy ] : No proxies.{Style.RESET_ALL}")
            
            response_activity = get_activity(raw_auth, proxy)
            if response_activity:
                print(f"{Fore.GREEN}[ Referral ] : Applied{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}[ Referral ] : Failed to Apply referral{Style.RESET_ALL}")
            # Fetch and print rank and earned before checking power
            rank, earned = get_metrics(raw_auth, proxy)
            print(f"{Fore.BLUE+Style.BRIGHT}[ Rank ] : {rank}{Style.RESET_ALL}")
            print(f"{Fore.GREEN+Style.BRIGHT}[ Balance ] : {earned}{Style.RESET_ALL}")
            power_ok, current_power, power_capacity = check_power(raw_auth, proxy)
            if power_ok:
                print(f"{Fore.GREEN}[ Power ] : {current_power}/{power_capacity}{Style.RESET_ALL}")
                if current_power >= 1000:
                    success, response = post_request(raw_auth, proxy)
                    if success:
                        hivera_balance = response.get('result', {}).get('profile', {}).get('HIVERA', 0)
                        print(f"{Fore.GREEN}[ Miner ] : Mining successful! Balance: {hivera_balance}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}[ Miner ] : Request failed. Response: {response}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}[ Miner ] : Skipping. Power is low{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}[ Power ]: Power is low{Style.RESET_ALL}")
            
            time.sleep(5)

            if use_proxy and len(proxies) > 1:
                proxy_index += 1

        animated_loading(60)
