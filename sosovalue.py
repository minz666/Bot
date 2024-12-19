import requests
import time
from faker import Faker
from colorama import Fore, Style, init
import re
from bs4 import BeautifulSoup

init(autoreset=True)
fake = Faker()

# Global headers
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en",
    "content-type": "application/json;charset=UTF-8",
    "priority": "u=1, i",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-device": "Mobile Safari/16.6#iOS/16.6",
    "Referer": "https://sosovalue.com/",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}

MAIL_TM_BASE = "https://api.mail.tm"

def create_temp_email():
    # Create an account on Mail.tm
    # Generate a random username and use a fixed password
    # Note: Mail.tm does not require domain selection, it gives you the domain.
    username = fake.user_name()
    email_address = f"{username}@freesourcecodes.com"
    account_data = {
        "address": email_address,
        "password": "@Pukimai123"
    }
    resp = requests.post(f"{MAIL_TM_BASE}/accounts", json=account_data)
    if resp.status_code == 201:
        # Account created successfully
        account_info = resp.json()
        # Now login to get the token
        token = login_temp_email(account_info["address"], account_data["password"])
        if token:
            print("Temporary email created:", account_info["address"])
            return account_info["address"], account_data["password"], token
        else:
            print("Failed to login and obtain token.")
            return None, None, None
    else:
        print("Failed to create temporary email.")
        return None, None, None

def login_temp_email(email, password):
    resp = requests.post(f"{MAIL_TM_BASE}/token", json={"address": email, "password": password})
    if resp.status_code == 200:
        token_data = resp.json()
        token = token_data.get("token")
        if token:
            print("Login successful, token obtained.")
            return token
        else:
            print("Failed to login and obtain token:", token_data)
            return None
    else:
        print("Failed to login:", resp.status_code, resp.text)
        return None

def send_otp(email, password):
    username = fake.user_name()  # Generate a random username
    url = "https://gw.sosovalue.com/usercenter/email/anno/sendRegisterVerifyCode/V2"
    body = {
        "password": password,
        "rePassword": password,
        "username": username,
        "email": email
    }
    response = requests.post(url, headers=HEADERS, json=body)
    return response.json(), username

def verify_otp(username, email, password, verify_code, invitation_code):
    url = "https://gw.sosovalue.com/usercenter/user/anno/v3/register"
    body = {
        "password": password,
        "rePassword": password,
        "username": username,
        "email": email,
        "verifyCode": verify_code,
        "invitationCode": invitation_code,
        "invitationFrom": None
    }
    response = requests.post(url, headers=HEADERS, json=body)
    return response.json()

def update_username(token):
    new_username = fake.user_name()
    url = "https://gw.sosovalue.com/usercenter/personal/v3/updateUsername"
    headers = HEADERS.copy()
    headers["authorization"] = f"Bearer {token}"
    body = {"username": new_username}
    response = requests.put(url, json=body, headers=headers)
    
    if response.status_code == 200:
        print(Fore.RESET + '[ ' + Fore.GREEN + 'SUCCESS' + Fore.RESET + ' ] ' + 
              'Username updated successfully to ' + Fore.GREEN + str(new_username) + Fore.RESET + '.')
        return response.json()
    else:
        print(Fore.RESET + '[ ' + Fore.RED + 'ERROR' + Fore.RESET + ' ] ' + 
              f'Failed to update username. Status code: ' + Fore.RED + str(response.status_code) + Fore.RESET)
        return None

def save_to_file(file_path, data):
    with open(file_path, 'a') as file:
        file.write(data + "\n")

def print_welcome_message():
    print(Fore.WHITE + r"""
          
█▀▀ █░█ ▄▀█ █░░ █ █▄▄ █ █▀▀
█▄█ █▀█ █▀█ █▄▄ █ █▄█ █ ██▄
          """)
    print(Fore.GREEN + Style.BRIGHT + "SosoValue REFF")
    print(Fore.YELLOW + Style.BRIGHT + "Free Konsultasi Join Telegram Channel: https://t.me/gsc_lobby")
    print(Fore.BLUE + Style.BRIGHT + "Buy me a coffee :) 0823 2367 3487 GOPAY / DANA")
    print(Fore.RED + Style.BRIGHT + "NOT FOR SALE ! Ngotak dikit bang. Ngoding susah2 kau tinggal rename :)\n\n")

def extract_verification_code(email_body):
    pattern = re.compile(r'Your verification code is:.*?>\s*(\d+)\s*<', re.IGNORECASE | re.DOTALL)
    match = pattern.search(email_body)
    if match:
        code = match.group(1)
      
        return code
    else:
        
        return None

def wait_for_verification_code(email, token, timeout=120, interval=5):
    # For mail.tm, we need to:
    # - GET /messages with Authorization: Bearer <token>
    # - Check if there's a message containing "SoSoValue"
    # - If yes, GET /messages/{id} to get the HTML and extract code
    headers = {"Authorization": f"Bearer {token}"}
    start_time = time.time()

    while True:
        resp = requests.get(f"{MAIL_TM_BASE}/messages", headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            messages = data.get("hydra:member", [])
            for message in messages:
                if "SoSoValue" in message.get('subject', ''):
                    # Fetch message details
                    msg_id = message["id"]
                    msg_resp = requests.get(f"{MAIL_TM_BASE}/messages/{msg_id}", headers=headers)
                    if msg_resp.status_code == 200:
                        msg_data = msg_resp.json()
                        html_content = msg_data.get("html")
                        if isinstance(html_content, list):
                            html_content = "".join(html_content)
                        elif not html_content:
                            # fallback to text
                            html_content = msg_data.get("text")
                            if isinstance(html_content, list):
                                html_content = "".join(html_content)

                        # If we have HTML content, we parse it
                        if html_content:
                            # Print the entire email body for debugging
                            # Convert HTML to text that we can search for the code
                            soup = BeautifulSoup(html_content, "html.parser")
                            email_body = soup.get_text()
                 
                            code = extract_verification_code(html_content)
                            if code:
                                return code

        if time.time() - start_time > timeout:
            print(Fore.RESET + '[ ' + Fore.RED + 'ERROR' + Fore.RESET + ' ] ' + 
                  'Timeout waiting for verification code from ' + email)
            return None
        time.sleep(interval)

def main():
    print_welcome_message()
    password = "I1N1a2FyYWphMTIz"
    invitation_code = "XXXXX"  # Replace with actual code
    output_file_path = 'info_akun.txt'

    number_of_accounts = 100  # How many accounts do you want to create?

    for index in range(1, number_of_accounts + 1):
        # Create a new email using mail.tm
        email, mail_password, token = create_temp_email()
        if not email or not token:
            print(Fore.RESET + '[ ' + Fore.RED + 'ERROR' + Fore.RESET + ' ] ' + "Failed to create and login to temporary email.")
            continue

        print(Fore.RESET + '[ ' + Fore.MAGENTA + 'DEBUG' + Fore.RESET + ' ]' + 
              ' Proses ' + Fore.MAGENTA + str(index) + Fore.RESET + '/' + Fore.GREEN + str(number_of_accounts) + Fore.RESET)
        
        result, username = send_otp(email, password)
        if result.get('code') == 0 and result.get('data') == True:
            print(Fore.RESET + '[ ' + Fore.GREEN + 'SUCCESS' + Fore.RESET + ' ]' + 
                  ' Mengirim OTP ke ' + Fore.GREEN + email + Fore.RESET)

            print(Fore.RESET + '[ ' + Fore.BLUE + 'INFO' + Fore.RESET + ' ] ' + 
                  'Menunggu kode verifikasi masuk ke ' + Fore.BLUE + email + Fore.RESET + ' ...')
            
            verify_code = wait_for_verification_code(email, token)
            print("[DEBUG] Verification code before sending to verify_otp:", verify_code)
            if verify_code is None:
                print(Fore.RESET + '[ ' + Fore.RED + 'FAILED' + Fore.RESET + ' ]' + 
                      ' Tidak mendapat kode verifikasi untuk ' + Fore.RED + email + Fore.RESET)
                continue

            # Proceed with OTP verification
            result = verify_otp(username, email, password, verify_code, invitation_code)
            if result.get('code') == 0 and result.get('data'):
                data = result['data']
                email_used = data.get('email', email)
                tid = result.get('tid', '')
                username_used = data.get('username', '')
                token_resp = data.get('token', '')
                refresh_token = data.get('refreshToken', '')

                formatted_data = f"{email_used}|{tid}|{username_used}|{token_resp}|{refresh_token}|"
                save_to_file(output_file_path, formatted_data)

                print(Fore.RESET + '[ ' + Fore.GREEN + 'SUCCESS' + Fore.RESET + ' ]' + 
                      ' Verify OTP ' + Fore.GREEN + email_used + Fore.RESET + ' berhasil')

                # Update username after successful registration
                update_username(token_resp)

                # Wait for 5 seconds after each account process
                print(Fore.RESET + '[ ' + Fore.WHITE + 'INFO' + Fore.RESET + ' ]' + ' Wait bang rehat dulu\n')
                time.sleep(5)
            else:
                print(Fore.RESET + '[ ' + Fore.RED + 'FAILED' + Fore.RESET + ' ] ' + 
                      ' Verification failed for ' + Fore.RED + str(email) + Fore.RESET + ': ' + 
                      Fore.RED + str(result) + Fore.RESET)
        else:
            print(Fore.RESET + '[ ' + Fore.RED + 'FAILED' + Fore.RESET + ' ] ' + 
                  ' Gagal mengirim OTP ke ' + Fore.RED + str(email) + Fore.RESET + ': ' + 
                  Fore.RED + str(result.get('msg', 'Unknown error')) + Fore.RESET)

    print(Fore.RESET + '[ ' + Fore.WHITE + 'INFO' + Fore.RESET + ' ] ' + 
          ' Semua proses telah selesai.')

if __name__ == "__main__":
    main()
