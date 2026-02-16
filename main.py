import argparse
import config
from nihongoScraper import scraper   

def main():
    parser = argparse.ArgumentParser(description="Fetch Japanese words and save them locally.")
    parser.add_argument("word", help="Word in romaji or English")
    parser.add_argument("-v", "--verb",
                        action="store_true",
                        help="Fetch verb conjugations for the provided word")
    args = parser.parse_args()

    try:
        if (args.verb): 
            print(f"Verb is passed -> {args.word} -> Fetching...")
            fetchedPage = scraper.fetchVerbConjugationsPage(args.word)
            conjugations = scraper.parse_verb_conjugations(fetchedPage)

            scraper.update_verb_data('data.json', f"{config.VERBS_DIR}/{args.word}.html", args.word)
        else:
            print(f"Searching for: {args.word}...")
            url = f"{config.JISHO_URL}/{args.word}"
            fetched_page = scraper.fetchPage(url)
            
            if fetched_page:
                scraper.saveJson(args.word, fetched_page)
                print(f"Successfully saved '{args.word}' to data.json")
            else:
                print(f"Could not find data for '{args.word}'.") 
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
