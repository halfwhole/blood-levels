import os
import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup

URL = 'https://www.redcross.sg'
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'blood_levels.log')

current_time = datetime.now().replace(microsecond=0).isoformat()

page = requests.get(URL)
soup = BeautifulSoup(page.text, 'html.parser')

last_updated = soup.find(class_='last_update').text.split(': ')[1]

pos = soup.find('div', class_='blood_bank_level positives').find_all('div', class_='human')
neg = soup.find('div', class_='blood_bank_level negatives').find_all('div', class_='human')

def parse_human(item):
    blood_type = item.find('span', class_='blood_text').text
    style = item.find('div', class_='fill_humam')['style']
    blood_level_percentage = re.search('height: (.*?)%;', style).group(1)
    blood_level_fraction = int(blood_level_percentage) / 100
    return "%s=%.2f" % (blood_type, blood_level_fraction)

blood_levels = [parse_human(item) for category in [pos, neg] for item in category]
blood_levels_string = ','.join(blood_levels)

with open(OUTPUT_FILE, 'a') as f:
    f.write('----------\n')
    f.write('Executed at: %s\n' % current_time)
    f.write('Last blood stock update: %s\n' % last_updated)
    f.write(blood_levels_string + '\n')
