import requests
from bs4 import BeautifulSoup
import random
import re

# Send a GET request to the website
r = requests.get('https://bishalsarang.github.io/Leetcode-Questions/out.html')

# Parse the HTML content
soup = BeautifulSoup(r.content, "html.parser")

# Find all question titles and descriptions
questions = soup.find_all("div", class_="content__u3I1 question-content__JfgR")

# Select a random question
random_question = random.choice(questions)

# Extract question title
title = random_question.find_previous_sibling("div", id="title").text.strip()
print("Title:", title)

# Extract question description and remove problematic Unicode characters
description = random_question.find("div").text.strip()
description_cleaned = description.replace('\u230a', '')  # Replace problematic Unicode character
print("Description:", description_cleaned.encode("utf-8"))

# Construct the problem link
title_with_hyphens = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '-').lower()
problem_link = f"https://leetcode.com/problems/{title_with_hyphens}"
link_without_number = re.sub(r'^\d+-', '', title_with_hyphens)
link_without_number = "https://leetcode.com/problems/"+link_without_number
print("Problem Link:", link_without_number)
