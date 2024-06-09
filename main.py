import os
import random
import time
import warnings
import subprocess
import sys
import platform
import urllib.request
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pystyle import Center, Colors, Colorate

warnings.filterwarnings("ignore", category=DeprecationWarning)

SETTINGS_FILE = 'settings.txt'
PROXY_SERVERS = [
    'https://www.blockaway.net', 'https://www.croxyproxy.com',
    'https://www.croxyproxy.rocks', 'https://www.croxy.network',
    'https://www.croxy.org', 'https://www.youtubeunblocked.live',
    'https://www.croxyproxy.net'
]
VALID_PLATFORMS = ['twitch', 'youtube', 'kick']

def install_requirements():
    """Install required packages from requirements.txt."""
    print(Colors.yellow + "Checking requirements - libraries... ⏳")
    try:
        with open('requirements.txt', 'r') as req_file:
            requirements = req_file.readlines()
        for req in requirements:
            subprocess.check_call([sys.executable, "-m", "pip", "install", req.strip()], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(Colors.green + "Libraries installed successfully! ✅")
    except Exception as e:
        print(Colors.red + f"Error installing requirements: {e}")

def save_settings(streaming_platform, username_or_url, set_160p):
    """Save user settings to a file."""
    with open(SETTINGS_FILE, 'w') as file:
        file.write(f"Platform: {streaming_platform}\n")
        file.write(f"Username or URL: {username_or_url}\n")
        file.write(f"Set 160p: {set_160p}\n")

def load_settings():
    """Load user settings from a file."""
    try:
        with open(SETTINGS_FILE, 'r') as file:
            lines = file.readlines()
            if len(lines) >= 3:
                streaming_platform = lines[0].split(': ')[1].strip()
                username_or_url = lines[1].split(': ')[1].strip()
                set_160p = lines[2].split(': ')[1].strip()
                return streaming_platform, username_or_url, set_160p
    except Exception:
        pass
    return None, None, None

def set_stream_quality(driver, quality):
    """Set the stream quality to 160p if required."""
    if quality.lower() == "yes":
        element_xpath = "//div[@data-a-target='player-overlay-click-handler']"
        element = driver.find_element(By.XPATH, element_xpath)
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()

        settings_button = driver.find_element(By.XPATH, "//button[@aria-label='Settings']")
        settings_button.click()

        wait = WebDriverWait(driver, 10)
        quality_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Quality']")))
        quality_option.click()

        time.sleep(15)

        quality_levels = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'video-quality-option')]")))
        target_quality = "160p"
        for level in quality_levels:
            if target_quality in level.text:
                level.click()
                break

def get_user_input():
    """Get user input for streaming platform, Twitch username or URL, and stream quality preference."""
    while True:
        streaming_platform = input(Colorate.Vertical(Colors.green_to_blue, "Enter the platform (twitch/youtube/kick): ")).lower()
        print('')
        if streaming_platform in VALID_PLATFORMS:
            break
        print(Colorate.Vertical(Colors.red_to_yellow, "Invalid input. Please enter 'twitch', 'youtube', or 'kick'."))
        print('')
    
    if streaming_platform == "youtube":
        username_or_url = input(Colorate.Vertical(Colors.green_to_blue, "Enter the full YouTube URL (e.g https://www.youtube.com/watch?v=03nrv09T7bs): "))
    else:
        username_or_url = input(Colorate.Vertical(Colors.green_to_blue, "Enter your channel name (e.g ninja): "))
    print('')
    set_160p = input(Colorate.Vertical(Colors.purple_to_red, "Do you want to set the stream quality to 160p (recommended)? (yes/no): "))
    if streaming_platform != "twitch":
        print(Colors.red)
        print("Currently 160p is only supported on Twitch! Defaulting to regular quality.")
        print(Colors.reset)
        set_160p = "no"
    return streaming_platform, username_or_url, set_160p

def is_chrome_installed():
    """Check if Chrome is installed."""
    chrome_paths = {
        'Windows': ['C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', 
                    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'],
        'Darwin': ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'],
        'Linux': ['/usr/bin/google-chrome', '/usr/local/bin/google-chrome']
    }
    os_name = platform.system()
    for path in chrome_paths.get(os_name, []):
        if os.path.exists(path):
            return True
    return False

def initialize_driver(os_name):
    """Initialize the Selenium WebDriver with the appropriate ChromeDriver."""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument("--lang=en")
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver_paths = {
        'Windows': 'ChromeDrivers/windows/chromedriver.exe',
        'Darwin': 'ChromeDrivers/mac/chromedriver',
        'Linux': 'ChromeDrivers/linux/chromedriver'
    }
    
    driver_path = driver_paths.get(os_name)
    if driver_path is None:
        print(Colors.red + "Unsupported operating system for ChromeDriver.")
        exit()

    try:
        return webdriver.Chrome(service=Service(driver_path), options=chrome_options)
    except Exception as e:
        print(Colors.red + f"Could not initialize ChromeDriver: {e}")
        exit()

def clear_screen(os_name):
    """Clear the terminal screen."""
    if os_name == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

def set_terminal_title(os_name, title):
    """Set the terminal title."""
    if os_name == 'Windows':
        os.system(f'title {title}')
    else:
        sys.stdout.write(f"\x1b]2;{title}\x07")

def display_banner():
    """Display the program banner and announcement."""
    os_name = platform.system()
    set_terminal_title(os_name, "Duerme - Chimera Bot")
    print(Colorate.Vertical(Colors.purple_to_blue, Center.XCenter("""
           
                                     ██████╗██╗  ██╗██╗███╗   ███╗███████╗██████╗  █████╗ 
                                    ██╔════╝██║  ██║██║████╗ ████║██╔════╝██╔══██╗██╔══██╗
                                    ██║     ███████║██║██╔████╔██║█████╗  ██████╔╝███████║
                                    ██║     ██╔══██║██║██║╚██╔╝██║██╔══╝  ██╔══██╗██╔══██║
                                    ╚██████╗██║  ██║██║██║ ╚═╝ ██║███████╗██║  ██║██║  ██║
                                    ╚═════╝╚═╝  ╚═╝╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝                                     
                                           
                                         THE AIO TWITCH, YOUTUBE, & KICK VIEW BOT                                
                                                           
                                                             @duerme    
                                                                  """)))
    announcement = "I AM NOT RESPONSIBLE FOR ANY MALICIOUS ACTIONS TAKEN BY USERS WHO DECIDE TO USE THIS PROGRAM. PLEASE BE SAFE AND RESPONSIBLE."
    print("")
    print(Colors.red, Center.XCenter("ANNOUNCEMENT"))
    print(Colors.yellow, Center.XCenter(f"{announcement}"))
    print("")
    print("")

def main():
    install_requirements()
    display_banner()
    proxy_url = random.choice(PROXY_SERVERS)
    print('')

    os_name = platform.system()
    print(Colors.purple, Center.XCenter(f"OS Detected: {os_name}"))

    print('')

    if not is_chrome_installed():
        print(Colors.red + "Google Chrome is not installed. Please install Google Chrome and try again.")
        exit()

    print(Colors.yellow + "Proxy servers are randomly selected every time!")
    print('')

    streaming_platform, username_or_url, set_160p = load_settings()
    if streaming_platform is None or username_or_url is None or set_160p is None:
        streaming_platform, username_or_url, set_160p = get_user_input()
        save_settings(streaming_platform, username_or_url, set_160p)
    else:
        use_settings = input(Colorate.Vertical(Colors.green_to_blue, "Do you want to use your saved settings? (yes/no): "))
        print('')
        if use_settings.lower() == "no":
            streaming_platform, username_or_url, set_160p = get_user_input()
            save_settings(streaming_platform, username_or_url, set_160p)
    
    print('')
    proxy_count = int(input(Colorate.Vertical(Colors.cyan_to_blue, "Number of users that you want to send: ")))
    print('')
    clear_screen(os_name)
    display_banner()
    print(Colors.green, Center.XCenter("Viewers are being sent. Please be patient as this takes some time. If the viewers do not arrive, restart the program and try again."))
    print(Colors.reset)

    driver = initialize_driver(os_name)
    driver.get(proxy_url)

    for _ in range(proxy_count):
        random_proxy_url = random.choice(PROXY_SERVERS)
        driver.execute_script("window.open('" + random_proxy_url + "')")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(random_proxy_url)

        text_box = driver.find_element(By.ID, 'url')
        if streaming_platform == "youtube":
            text_box.send_keys(username_or_url)
        elif streaming_platform == "twitch":
            text_box.send_keys(f'www.{streaming_platform}.tv/{username_or_url}')
        else: 
            text_box.send_keys(f'www.{streaming_platform}.com/{username_or_url}')
        text_box.send_keys(Keys.RETURN)
        time.sleep(10)

    set_stream_quality(driver, set_160p)
    input(Colorate.Vertical(Colors.red_to_blue, "Your viewers/views are loading...\n If you close the program, your viewers will disappear."))
    driver.quit()

if __name__ == '__main__':
    main()
