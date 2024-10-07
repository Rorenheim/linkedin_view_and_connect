#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import random
import time
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
from random import shuffle
from os.path import join, dirname
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load environment variables from .env file
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Configurable Constants from .env
EMAIL = os.getenv("EMAIL", '')
PASSWORD = os.getenv("PASSWORD", '')
COUNTRY_FILTER = os.getenv("COUNTRY_FILTER", 'Germany')

# Other constants (these can remain hardcoded)
CONNECT_WITH_USERS = True
RANDOMIZE_CONNECTING_WITH_USERS = True
VERBOSE = True

# Define the search groups
SEARCH_GROUPS = {
    "1": "https://www.linkedin.com/search/results/people/?geoUrn=%5B%22101282230%22%5D&keywords=CPO%20OR%20Chief%20Product%20Officer%20OR%20VP%20of%20Product%20OR%20Chief%20Technology%20Officer&origin=FACETED_SEARCH",
    "2": "https://www.linkedin.com/search/results/people/?geoUrn=%5B%22101282230%22%5D&keywords=HR%20OR%20Recruiter%20OR%20Talent%20Acquisition%20Manager%20OR%20Head%20of%20Talent%20Acquisition&origin=FACETED_SEARCH",
    "3": "https://www.linkedin.com/search/results/people/?geoUrn=%5B%22101282230%22%5D&keywords=Product%20Manager%20OR%20Group%20Product%20Manager%20OR%20Director%20of%20Product%20OR%20Head%20of%20Product%20OR%20Product%20Lead&origin=FACETED_SEARCH"
}

def launch():
    """
    Launch the LinkedIn bot using Firefox.
    """

    # Check if the file 'visitedUsers.txt' exists, otherwise create it
    if not os.path.isfile('visitedUsers.txt'):
        with open('visitedUsers.txt', 'w') as visitedUsersFile:
            pass

    print('Launching Firefox Browser')

    # Use GeckoDriverManager without executable_path
    browser = webdriver.Firefox(service=webdriver.firefox.service.Service(GeckoDriverManager().install()))

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
    linked_in_bot(browser, search_url)

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

def linked_in_bot(browser, search_url):
    """
    Run the LinkedIn Bot.
    browser: the selenium driver to run the bot with.
    search_url: the URL to use for searching LinkedIn profiles.
    """
    profiles_queued = []
    visited_count = 0
    current_page = 1

    # Load search URL
    browser.get(search_url)
    time.sleep(5)

    print('Searching for profiles to view based on job title and country filter...\n')

    # Infinite loop to navigate through search results pages
    while True:
        soup = BeautifulSoup(browser.page_source, "html.parser")
        profiles_queued.extend(get_new_profile_urls(soup, profiles_queued))
        profiles_queued = list(set(profiles_queued))  # Remove duplicates

        print(f"\nProfiles to visit queued: {len(profiles_queued)}")

        while profiles_queued:
            shuffle(profiles_queued)
            profile_id = profiles_queued.pop()
            visited_count += 1

            # Fix: Check if profile_id is already a full URL or just a path
            if profile_id.startswith('http'):
                profile_url = profile_id
            else:
                profile_url = 'https://www.linkedin.com' + profile_id

            try:
                print(f"Visiting profile: {profile_url}")
                browser.get(profile_url)
                time.sleep(3)

                # Connect with every 10th user
                if CONNECT_WITH_USERS and visited_count % 10 == 0:
                    connect_with_user(browser)

                with open('visitedUsers.txt', 'a') as visitedUsersFile:
                    visitedUsersFile.write(str(profile_id) + '\n')

            except Exception as e:
                if VERBOSE:
                    print(f"Failed to visit profile {profile_url}: {e}")

            time.sleep(5)

        print('\nNo more profiles to visit on this page, trying the next page...\n')
        # Go to the next page of search results
        current_page += 1
        next_page_url = f"{search_url}&page={current_page}"
        try:
            print(f"Navigating to next page: {next_page_url}")
            browser.get(next_page_url)
            time.sleep(5)
        except Exception as e:
            print(f'No more pages of search results or an error occurred: {e}. Ending script.')
            break

def connect_with_user(browser):
    """
    Connect with the user viewing if their job title matches your list of roles and they are in the correct country.
    """
    soup = BeautifulSoup(browser.page_source, "html.parser")
    job_title_matches = False
    country_matches = False

    # Check if the job title matches
    for h2 in soup.find_all('h2'):
        for job in JOBS_TO_CONNECT_WITH:
            if job.upper() in h2.get_text().upper():
                job_title_matches = True
                break

    # Check if the country matches (new feature)
    for span in soup.find_all('span', {'class': 'text-body-small'}):
        if COUNTRY_FILTER.lower() in span.get_text().lower():
            country_matches = True
            break

    if job_title_matches and country_matches:
        try:
            if VERBOSE:
                print(f"Job title matches and country is {COUNTRY_FILTER}. Sending an invitation to connect.")
            connect_button = browser.find_element(By.XPATH, '//button[text()="Connect"]')
            connect_button.click()
            time.sleep(random.randrange(2, 4))

            # Add a note to the connection request
            add_note_button = browser.find_element(By.XPATH, '//button[text()="Add a note"]')
            add_note_button.click()
            time.sleep(2)

            note_textarea = browser.find_element(By.XPATH, '//textarea[@name="message"]')
            note_text = """Hello,

            I’m expanding my professional network and came across your profile. I’m always interested in connecting with others in the industry and thought it would be great to add you to my network.

            Looking forward to staying connected.

            Best,
            Paul"""
            note_textarea.send_keys(note_text)
            time.sleep(2)

            send_button = browser.find_element(By.XPATH, '//button[text()="Send"]')
            send_button.click()
            print("Connection request sent successfully.")
        except (NoSuchElementException, ElementNotInteractableException) as e:
            if VERBOSE:
                print(f"Failed to send connection request or only able to follow: {e}")
    else:
        if VERBOSE:
            if not job_title_matches:
                print("Job title does not match.")
            if not country_matches:
                print(f"Country does not match. Expected: {COUNTRY_FILTER}")

def get_new_profile_urls(soup, profiles_queued):
    """
    Get new profile URLs to add to the navigation queue.
    """
    with open('visitedUsers.txt', 'r') as visitedUsersFile:
        visited_users = [line.strip() for line in visitedUsersFile]

    profile_urls = []

    for profile in soup.find_all('a', {'href': True}):
        profile_url = profile['href']
        if '/in/' in profile_url and profile_url not in visited_users and profile_url not in profiles_queued:
            profile_urls.append(profile_url)

    return list(set(profile_urls))

if __name__ == '__main__':
    launch()