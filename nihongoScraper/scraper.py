import config 

import os 
import re
import json
import requests 
from bs4 import BeautifulSoup 

def fetchPage(url: str) -> str: 
    fileName = url.split("/")[-1] + ".html"
    if os.path.exists(f"{config.WORDS_DIR}/{fileName}"): 
        print("Status: Fetching from cache")
        with open(f"{config.WORDS_DIR}/{fileName}", "r") as file: 
            return file.read()

    print("Status: Fetching from web")
    page = requests.get(url).text
    saveText(fileName, page, config.WORDS_DIR)
    return page 

def saveText(fileName: str, text: str, dir: str) -> bool: 
    try: 
        with open(f"{dir}/{fileName}", "w") as page: 
            page.write(text)
    except Exception as error: 
        print(f"Error: {error}")
        return False 
    return True 


def saveJson(romaji: str, fetchedPage: str) -> bool:
    parser = BeautifulSoup(fetchedPage, "html.parser")

    primary_div = parser.find(id="primary")

    hiragana_sounds = primary_div.find('span', {"class": "furigana"})
    hiragana = "" 
    for hira in hiragana_sounds.children: 
        hiragana += hira.text.strip()

    kanji = primary_div.find('span', { "class": 'text' }).text.strip()

    meaning = primary_div.find('span', {"class": 'meaning-meaning'}).text.strip()

    group = primary_div.find('div', {'class': "meaning-tags"}).text.strip()

    print(f"{romaji} -> {hiragana} -> {kanji} -> {meaning} -> {group}")

    # Let's first open the data.json file 

    with open("data.json", 'r+') as file:
        # Load existing data into a dictionary

        file_data = json.load(file)

        if (romaji in file_data):
            return True
       
        file_data[romaji] = {'hiragana': hiragana, 'kanji': kanji, 'meaning': meaning, 'group': group}
        
        # Move the cursor to the beginning of the file
        file.seek(0)
        
        # Write the updated data back to the file
        json.dump(file_data, file, indent=4, ensure_ascii=False)

    return True

def fetchVerbConjugationsPage(word: str) -> str : 
    params = {
        'txtVerb': word,
        'Go': 'Conjugate'
    }

    filename = f"{word}.html"
    if os.path.exists(f"{config.VERBS_DIR}/{filename}"): 
        with open(f"{config.VERBS_DIR}/{filename}", "r") as file: 
            return file.read()

    url_fetched = requests.get(config.VERB_CONJUGATOR, params=params).text
    saveText(filename, url_fetched, config.VERBS_DIR)

    return url_fetched

def parse_verb_conjugations(html_content):
    """
    Precision Scraper for Ultra-Guji Verb Tables.
    Extracts Japanese conjugations while filtering out English example sentences.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    conjugations = {}
    
    # Regex to identify Japanese characters (Hiragana, Katakana, Kanji)
    jp_regex = re.compile(r'[\u3040-\u30ff\u4e00-\u9faf]')

    def extract_jp(cell):
        if not cell: return ""
        # Merge Romaji and Kanji with a space for readability
        text = cell.get_text(" ", strip=True).replace('?', '').strip()
        # Clean up internal extra whitespace/newlines
        text = re.sub(r'\s+', ' ', text)
        return text if jp_regex.search(text) else ""

    rows = soup.find_all('tr')
    current_tense = None

    for row in rows:
        cells = row.find_all(['td', 'th'])
        if len(cells) < 2:
            continue

        col0 = cells[0].get_text(strip=True).replace('?', '')
        col1_text = cells[1].get_text(strip=True).lower()
        
        # 1. Tense Header Tracking
        if col0 and "polite" not in col0.lower() and "plain" not in col0.lower():
            # Stop if we hit the "Example Sentences" or "Translation" sections
            if len(col0) > 30 or "is there" in col0.lower() or "sushi" in col0.lower():
                break
            current_tense = col0
            if current_tense not in conjugations:
                conjugations[current_tense] = {}

        if not current_tense:
            continue

        # 2. Determine Sub-type (Plain/Polite)
        is_polite = "polite" in col0.lower() or "polite" in col1_text
        sub_type = "polite" if is_polite else "plain"
        
        if sub_type not in conjugations[current_tense]:
            conjugations[current_tense][sub_type] = {"positive": "", "negative": ""}

        # 3. Scanning Columns
        # Scans cells to find the relevant Japanese verb forms
        extracted_values = []
        for i in range(1, len(cells)):
            val = extract_jp(cells[i])
            # Filter out the labels 'plain' and 'polite' themselves
            if val and val.lower() not in ["plain", "polite"]:
                extracted_values.append(val)

        # 4. Content-Aware Assignment
        for val in extracted_values:
            # Check for negative markers
            is_neg = False
            v_low = val.lower()
            if any(m in v_low for m in ["masen", "nakatta"]):
                is_neg = True
            elif "nai" in v_low and "deshō" not in v_low and "desho" not in v_low:
                is_neg = True
            elif v_low.endswith(" na") or " na " in v_low or "nai de" in v_low:
                is_neg = True
            
            # Assignment
            target = "negative" if is_neg else "positive"
            
            # If multiple forms exist (e.g., presumptive), combine them or keep longest
            if not conjugations[current_tense][sub_type][target]:
                conjugations[current_tense][sub_type][target] = val
            elif val not in conjugations[current_tense][sub_type][target]:
                conjugations[current_tense][sub_type][target] += f" / {val}"

    # --- CLEANING SCRIPT ---
    cleaned_data = {}
    for tense, forms in conjugations.items():
        # 1. Clean up Verb Class and Stem (special formatting)
        if tense in ["Verb Class", "Stem"]:
            cleaned_data[tense] = forms
            continue

        # 2. Filter out keys that have no data or are example sentences
        # (Example sentences usually don't have a 'Polite' sub-key with data)
        has_plain = forms.get('plain', {}).get('positive') or forms.get('plain', {}).get('negative')
        has_polite = forms.get('polite', {}).get('positive') or forms.get('polite', {}).get('negative')
        
        if has_plain or has_polite:
            # Only add if it's an actual conjugation (not a long sentence)
            if len(tense) < 35:
                cleaned_data[tense] = forms

    return cleaned_data


def update_verb_data(json_filepath, html_filepath, verb_key):
    """
    Reads existing data.json and injects scraped conjugations into the specific verb key.
    """
    # 1. Load existing data
    try:
        with open(json_filepath, 'r', encoding='utf-8') as f:
            full_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Error: Could not read {json_filepath}")
        return

    # 2. Scrape the HTML
    try:
        with open(html_filepath, 'r', encoding='utf-8') as f:
            html_content = f.read()
            new_conjugations = parse_verb_conjugations(html_content)
    except FileNotFoundError:
        print(f"Error: {html_filepath} not found.")
        return

    # 3. Merge data into the specific verb key
    if verb_key in full_data:
        # We add a new field 'conjugations' to the existing object
        full_data[verb_key]['conjugations'] = new_conjugations
        print(f"Successfully updated conjugations for '{verb_key}'.")
    else:
        print(f"Warning: '{verb_key}' not found in JSON. Creating new entry.")
        full_data[verb_key] = {'conjugations': new_conjugations}

    # 4. Write back to data.json
    with open(json_filepath, 'w', encoding='utf-8') as f:
        json.dump(full_data, f, indent=4, ensure_ascii=False)
        print(f"File '{json_filepath}' has been updated.")

