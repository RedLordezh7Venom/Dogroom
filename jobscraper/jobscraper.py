from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import os
import sys

# Ensure the script uses UTF-8 encoding for output
sys.stdout.reconfigure(encoding='utf-8')

# Function to read the last posted date from the file
def read_last_posted_date(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            last_posted_date_str = file.read().strip()
            if last_posted_date_str:
                return datetime.strptime(last_posted_date_str, '%Y-%m-%d %H:%M:%S')
    return None

# Function to write the current date to the file
def write_current_date(file_path):
    with open(file_path, 'w') as file:
        current_date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        file.write(current_date_str)

# File to store the last posted date
file_path = 'last_posted_date.txt'

# List of URLs to check
urls = [
    'https://t.me/s/goyalarsh',
    'https://t.me/s/internfreak',
    'https://t.me/s/techwithmukulcode',
    'https://t.me/s/TechProgramMind_official',
    'https://t.me/s/gocareers',
    'https://t.me/s/riddhi_dutta',
    'https://web.telegram.org/k/#@yet_another_internship_finder'
]

# Read the last posted date from the file
last_posted_date = read_last_posted_date(file_path)

def keywords(content):
    if "company" in content or "hiring" in content or "role" in content or "location" in content or "link" in content:
        return True


# Iterate over each URL
for url in urls:
    # Send a GET request to the webpage
    response = requests.get(url)
    
    # Parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Find all job messages
    job_messages = soup.find_all("div", class_="tgme_widget_message_text js-message_text")
    
    # Iterate over each job message
    for message in job_messages:
        # Check if the message contains the word "company" or "hiring"
        if keywords(message.text.lower()):
            # Check if 12 hours have passed since the last post
            if last_posted_date is None or datetime.now() - last_posted_date >= timedelta(hours=12):
                # Print the entire post
                print("Job Post from", url)
                print(message.text.strip())
                print()
                
                # Update the last posted date to the current date and time
                write_current_date(file_path)
                
                # Since we're posting one message, we can break the loop
                break

# Save the current date and time after processing all URLs
write_current_date(file_path)
