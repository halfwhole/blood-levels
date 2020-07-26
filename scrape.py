import os
import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup

URL = 'https://www.redcross.sg'
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'blood_levels.csv')

def scrape_pos_neg_levels_last_updated():
    page = requests.get(URL)
    soup = BeautifulSoup(page.text, 'html.parser')
    pos = soup.find('div', class_='blood_bank_level positives').find_all('div', class_='human')
    neg = soup.find('div', class_='blood_bank_level negatives').find_all('div', class_='human')
    last_updated = soup.find(class_='last_update').text.split(': ')[1]
    return pos, neg, last_updated

def get_blood_levels(pos_levels, neg_levels):
    def parse_level(item):
        blood_type = item.find('span', class_='blood_text').text
        style = item.find('div', class_='fill_humam')['style']
        blood_level_percentage = re.search('height: (.*?)%;', style).group(1)
        blood_level_fraction = "%.2f" % (int(blood_level_percentage) / 100)
        return blood_type, blood_level_fraction

    blood_levels = dict(parse_level(item) for category in [pos_levels, neg_levels] for item in category)
    return blood_levels

def save_blood_levels_to_csv(blood_levels, execution_start_time, last_updated):
    blood_group_order = ['A+', 'B+', 'O+', 'AB+', 'A-', 'B-', 'O-', 'AB-']
    blood_levels_string = ','.join(blood_levels[blood_group] for blood_group in blood_group_order)
    file_exists = os.path.isfile(OUTPUT_FILE)

    with open(OUTPUT_FILE, 'a') as f:
        if not file_exists:
            f.write('Execution start time,Last blood stock update time,%s\n' % ','.join(blood_group_order))
        f.write('%s,%s,%s\n' % (execution_start_time, last_updated, blood_levels_string))

if __name__ == '__main__':
    execution_start_time = datetime.now().replace(microsecond=0).isoformat()
    pos_levels, neg_levels, last_updated = scrape_pos_neg_levels_last_updated()
    blood_levels = get_blood_levels(pos_levels, neg_levels)
    save_blood_levels_to_csv(blood_levels, execution_start_time, last_updated)
