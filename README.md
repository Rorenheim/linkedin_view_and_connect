
# LinkedIn Bot Project

## Credits
Many thanks to [@MattFlood7](https://github.com/MattFlood7) and [@klpod221](https://github.com/klpod221) whose ideas and code helped me to combine profile viewer and auto-connect in a single project.

## What's missing
1. Country and job positions is currently semi-hardcoded - replace URLs in SEARCH_GROUPS array to target needed country and roles
2. Originally autoconnect.py supposed to be a part of the linkedin_bot.py app, but I had a weird bug of skipping entire pages without visiting any profiles.

## Structure
This project consists of two main Python scripts that automate tasks on LinkedIn:
1. `linkedin_bot.py`: This script is designed for browsing profiles based on specific job titles and filters.
2. `autoconnect.py`: This script automatically sends connection requests to LinkedIn users, including a personalized message.
3. `.env`: Configuration file that stores your LinkedIn credentials and filter settings.

## Features
- **Profile Viewing (`linkedin_bot.py`)**:
  - Views profiles on LinkedIn based on job title and country filters.
  - Logs each visited profile to prevent revisiting the same profile.
  
- **Connection Requesting (`autoconnect.py`)**:
  - Sends connection requests automatically based on job titles and filters.
  - Adds a personalized note to the connection request.
  - Logs all connection requests to individual log files for each group of job titles.

## Prerequisites
- Python 3.x
- Selenium
- Firefox (with geckodriver)
- A LinkedIn account

### Required Python Packages
- `selenium`
- `webdriver_manager`
- `beautifulsoup4`
- `python-dotenv`

You can install the required packages using the following command:
```bash
pip install -r requirements.txt
```

## Project Structure

- **`linkedin_bot.py`**: 
  - This script views LinkedIn profiles that match specified job titles and filters by country. The script logs each visited profile to `visitedUsers.txt` to avoid visiting them again in the future.
  
- **`autoconnect.py`**: 
  - This script sends connection requests to LinkedIn users with a personalized message. The requests are sent based on job titles and country filters defined in the script. It logs all connection requests to log files (e.g., `group_1_requests.txt`, `group_2_requests.txt`).

- **`.env`**: 
  - This file contains environment variables, including your LinkedIn email, password, and country filter. It should be placed in the project root directory. Example:
  
  ```ini
  EMAIL=your_linkedin_email
  PASSWORD=your_linkedin_password
  COUNTRY_FILTER=Germany  # Example: Change this to the country you want to filter profiles by.
  ```

## Usage

### Step 1: Set Up Environment Variables
Create a `.env` file in the project directory with the following content:
```ini
EMAIL=your_linkedin_email
PASSWORD=your_linkedin_password
COUNTRY_FILTER=Germany
```

### Step 2: Run the Profile Viewing Bot
To start viewing profiles based on the criteria, run the following command:
```bash
python linkedin_bot.py
```

This will launch the Firefox browser, log into your LinkedIn account, and begin viewing profiles that match the selected group.

### Step 3: Run the Auto-Connect Bot
To automatically send connection requests, run the following command:
```bash
python autoconnect.py
```

This will launch the browser, log into LinkedIn, and start sending connection requests with a personalized message to users who match the job titles and country filters.

## Configuration

### Job Titles and Groups
You can modify the job titles and groups in both `linkedin_bot.py` and `autoconnect.py` by editing the `SEARCH_GROUPS` and `JOBS_TO_CONNECT_WITH` variables.

Example (in `autoconnect.py`):
```python
SEARCH_GROUPS = {
    "1": "https://www.linkedin.com/search/results/people/?geoUrn=%5B%22101282230%22%5D&keywords=CPO%20OR%20Chief%20Product%20Officer%20OR%20VP%20of%20Product%20OR%20Chief%20Technology%20Officer",
    "2": "https://www.linkedin.com/search/results/people/?geoUrn=%5B%22101282230%22%5D&keywords=HR%20OR%20Recruiter%20OR%20Talent%20Acquisition%20Manager",
    "3": "https://www.linkedin.com/search/results/people/?geoUrn=%5B%22101282230%22%5D&keywords=Product%20Manager%20OR%20Director%20of%20Product"
}
```

### Custom Messages
You can customize the message that is sent along with the connection request in `autoconnect.py`. Modify the `MESSAGE_TEMPLATE` variable:

```python
MESSAGE_TEMPLATE = """Hi %EMPLOYEE%,

I’m expanding my professional network and came across your profile. I’m always interested in connecting with others in the industry and thought it would be great to add you to my network.

Looking forward to staying connected.

Best,
Your Name"""
```

## Log Files
- **Visited Profiles**: The `linkedin_bot.py` script logs all visited profiles in a file called `visitedUsers.txt`. This file ensures that profiles are not revisited across different sessions.
- **Sent Requests**: Each connection request is logged in group-specific files, such as `group_1_requests.txt`, `group_2_requests.txt`, etc.

## License
This project is licensed under the MIT License.
