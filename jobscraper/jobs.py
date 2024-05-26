from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import os
import google.generativeai as genai
from dotenv import load_dotenv
import sys


# Load environment variables
load_dotenv()
TOKEN = os.environ.get('TOKEN')
GOOGLE_AI_KEY = os.environ.get('GOOGLE_AI_KEY')

# Configure the generative AI model
genai.configure(api_key=GOOGLE_AI_KEY)
text_generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 512,
}
safety_settings = [{
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
}, {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
}, {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
}, {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
}]
text_model = genai.GenerativeModel(model_name="gemini-pro",
                                   generation_config=text_generation_config,
                                   safety_settings=safety_settings)

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

# List of URLs
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

# Function to check if a message contains valid data based on keywords
def keywords(content):
    if "company" in content or "hiring" in content or "role" in content or "location" in content:
        if "role" in content:
            return True
    return False

# Function to parse the date string and add the current year
def parse_date(date_str, default_year=datetime.now().year):
    # Define the format of the input date string
    date_format = "%B %d"
    
    # Parse the input date string to get the month and day
    parsed_date = datetime.strptime(date_str, date_format)
    
    # Create a new datetime object with the default year and the parsed month and day
    full_date = datetime(default_year, parsed_date.month, parsed_date.day)
    
    return full_date

# Iterate over each URL
for url in urls:
    # Send a GET request to the webpage
    response = requests.get(url)
    
    # Parsing HTML content
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Find all job messages and date elements
    date_elements = soup.find_all("div", class_="tgme_widget_message_service_date")
    job_messages = soup.find_all("div", class_="tgme_widget_message_text js-message_text")
    
    # Find the bottom-most date element with the current date
    current_date = datetime.now()
    bottom_date_element = None
    for date_element in reversed(date_elements):
        date_str = date_element.text.strip()
        message_date = parse_date(date_str)
        if message_date.date() == current_date.date():
            bottom_date_element = date_element
            break
    
    # Find all job messages below the bottom date element
    if bottom_date_element:
        for message in bottom_date_element.find_all_next("div", class_="tgme_widget_message_text js-message_text"):
            if keywords(message.text.lower()):
                # Check if 12 hours have passed since the last post
                if last_posted_date is None or datetime.now() - last_posted_date >= timedelta(hours=12):
                    # Print post in JSON format
                    print("Job Post from", url)
                    prompt = f"Generate the following data in JSON form with the following format : {{MainData : {{Company: '',Role: '',Location: '',Link: '',}},   Additionals: {{// with any keys as per posting like batch,duration,type,salary}}}} {message.text}"
                    cleaned_text = text_model.generate_content(prompt)
                    print(cleaned_text.text.strip())
                    print()
                    
                    # Update last posted date to current date and time
                    write_current_date(file_path)
                    

# Save the current date and time after processing all URLs
write_current_date(file_path)
