#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import random
import time
import sys
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotInteractableException,
    TimeoutException,
    StaleElementReferenceException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Configurable Constants from .env
EMAIL = os.getenv("EMAIL", '')
PASSWORD = os.getenv("PASSWORD", '')
COUNTRY_FILTER = os.getenv("COUNTRY_FILTER", 'Germany')

# Other constants (these can remain hardcoded)
VERBOSE = True

# Define the search groups
SEARCH_GROUPS = {
    "1": "https://www.linkedin.com/search/results/people/?geoUrn=%5B%22101282230%22%5D&keywords=CPO%20OR%20Chief%20Product%20Officer%20OR%20VP%20of%20Product%20OR%20Chief%20Technology%20Officer&origin=FACETED_SEARCH",
    "2": "https://www.linkedin.com/search/results/people/?geoUrn=%5B%22101282230%22%5D&keywords=HR%20OR%20Recruiter%20OR%20Talent%20Acquisition%20Manager%20OR%20Head%20of%20Talent%20Acquisition&origin=FACETED_SEARCH",
    "3": "https://www.linkedin.com/search/results/people/?geoUrn=%5B%22101282230%22%5D&keywords=Product%20Manager%20OR%20Group%20Product%20Manager%20OR%20Director%20of%20Product%20OR%20Head%20of%20Product%20OR%20Product%20Lead&origin=FACETED_SEARCH"
}

# Message template
MESSAGE_TEMPLATE = """Hi %EMPLOYEE%,

I’m expanding my professional network and came across your profile. I’m always interested in connecting with others in the industry and thought it would be great to add you to my network.

Looking forward to staying connected.

Best,
Paul"""


def launch():
    """
    Launch the LinkedIn bot using Firefox.
    """
    print('Launching Firefox Browser')

    # Use GeckoDriverManager without executable_path
    browser = webdriver.Firefox(service=Service(GeckoDriverManager().install()))

    # Sign in to LinkedIn
    browser.get('https://linkedin.com/uas/login')
    time.sleep(2)

    email_element = browser.find_element(By.ID, 'username')
    email_element.send_keys(EMAIL)

    pass_element = browser.find_element(By.ID, 'password')
    pass_element.send_keys(PASSWORD)
    pass_element.submit()

    print('Signing in...')
    time.sleep(5)

    # Handle 2FA if present
    handle_two_factor_auth(browser)

    # Ask the user which group to work with
    print("Select the group to work with:")
    print("[1] High-Level Executives (CPO, Chief Product Officer, etc.)")
    print("[2] Talent and Recruiting Roles (HR, Recruiter, etc.)")
    print("[3] Product Management Roles (Product Manager, Director of Product, etc.)")
    group_choice = input("Enter the group number (1, 2, or 3): ")

    if group_choice not in SEARCH_GROUPS:
        print("Invalid choice. Exiting.")
        return

    search_url = SEARCH_GROUPS[group_choice]

    # Open log file for the chosen group
    log_file = f"group_{group_choice}_requests.txt"

    linked_in_bot(browser, search_url, log_file)


def handle_two_factor_auth(browser):
    """
    Handle LinkedIn Two-Factor Authentication if it is required.
    """
    try:
        # Wait and check for the 2FA input element
        time.sleep(5)
        two_factor_input = browser.find_element(By.ID, 'input__phone_verification_pin')

        # If 2FA is detected, prompt the user for the code
        if two_factor_input:
            two_factor_code = input("Enter the 2FA code sent to your device: ")
            two_factor_input.send_keys(two_factor_code)

            # Submit the 2FA code
            submit_button = browser.find_element(By.XPATH, '//button[@type="submit"]')
            submit_button.click()
            time.sleep(5)
            print("2FA Code submitted successfully.")

    except Exception as e:
        if VERBOSE:
            print(f"No 2FA code required or unable to find the 2FA input field. Error: {e}")


def linked_in_bot(browser, search_url, log_file):
    """
    Run the LinkedIn Bot.
    browser: the selenium driver to run the bot with.
    search_url: the URL to use for searching LinkedIn profiles.
    log_file: file path to log profiles sent connection requests.
    """
    requests_sent = 0
    current_page = 1
    MAX_REQUESTS = 100

    # Load search URL
    browser.get(search_url)
    time.sleep(5)

    print('Starting to send connection requests...\n')

    # While we have not reached the request limit
    while requests_sent < MAX_REQUESTS:
        print(f"Processing page {current_page}")

        # Scroll to the bottom to load all profiles
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Find all "Connect" buttons on the page
        try:
            connect_buttons = browser.find_elements(By.XPATH, '//button[.//span[text()="Connect"]]')
            if not connect_buttons:
                print("No connectable profiles found on this page.")
        except Exception as e:
            print(f"Error finding Connect buttons: {e}")
            break

        for btn in connect_buttons:
            if requests_sent >= MAX_REQUESTS:
                print("Reached 300 connection requests. Stopping.")
                browser.quit()
                sys.exit()

            try:
                btn_aria_label = btn.get_attribute("aria-label")
                user_name = btn_aria_label.split("Invite ")[1].split(" to connect")[0]
                first_name = user_name.split(' ')[0]
            except Exception:
                first_name = "there"

            try:
                # Click the Connect button
                browser.execute_script("arguments[0].click();", btn)
                time.sleep(5)

                # Click "Add a note"
                try:
                    add_note_button = WebDriverWait(browser, 5).until(
                        EC.element_to_be_clickable((By.XPATH, '//button[contains(@aria-label, "Add a note")]'))
                    )
                    browser.execute_script("arguments[0].click();", add_note_button)
                    time.sleep(5)
                except Exception as e:
                    print(f"Could not find 'Add a note' button for {user_name}: {e}")
                    # Close the dialog and continue
                    dismiss_dialog(browser)
                    continue

                # Type note
                try:
                    note_textarea = WebDriverWait(browser, 5).until(
                        EC.visibility_of_element_located((By.XPATH, '//textarea[@name="message"]'))
                    )
                    note_message = MESSAGE_TEMPLATE.replace('%EMPLOYEE%', first_name)
                    note_textarea.send_keys(note_message)
                    time.sleep(2)
                except Exception as e:
                    print(f"Could not find message textarea for {user_name}: {e}")
                    # Close the dialog and continue
                    dismiss_dialog(browser)
                    continue

                # Click Send
                try:
                    send_button = WebDriverWait(browser, 5).until(
                        EC.element_to_be_clickable((By.XPATH, '//button[contains(@aria-label, "Send")]'))
                    )
                    browser.execute_script("arguments[0].click();", send_button)
                    print(f"Connection request sent to {user_name}.")
                    requests_sent += 1

                    # Log the user name to the file
                    with open(log_file, "a") as f:
                        f.write(f"Connection request sent to {user_name}\n")

                except Exception as e:
                    print(f"Could not click 'Send' button for {user_name}: {e}")
                    # Close the dialog and continue
                    dismiss_dialog(browser)
                    continue

            except Exception as e:
                print(f"Could not send connection request to {user_name}: {e}")
                # Close the dialog
                dismiss_dialog(browser)
                continue

            # Wait 10 seconds regardless of success or failure
            time.sleep(10)

        print('Finished processing profiles on this page.')
        current_page += 1

        if requests_sent >= MAX_REQUESTS:
            print("Reached 300 connection requests. Stopping.")
            browser.quit()
            sys.exit()

        # Go to the next page
        next_page_url = f"{search_url}&page={current_page}"
        try:
            print(f"Navigating to next page: {next_page_url}")
            browser.get(next_page_url)
            time.sleep(5)
        except Exception as e:
            print(f'No more pages of search results or an error occurred: {e}. Ending script.')
            break

    print("Finished sending connection requests.")
    browser.quit()


def dismiss_dialog(browser):
    """
    Dismiss the open dialog to return to the main page.
    """
    try:
        close_button = browser.find_element(By.XPATH, '//button[@aria-label="Dismiss"]')
        browser.execute_script("arguments[0].click();", close_button)
        time.sleep(1)
    except Exception as e:
        if VERBOSE:
            print(f"Could not close the dialog: {e}")


if __name__ == '__main__':
    launch()
