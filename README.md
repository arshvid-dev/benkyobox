# BenkyoBox 🍱

> [!WARNING]
> **MAINTENANCE STATUS: UNMAINTAINED / AS-IS** > This project is not maintained on a regular basis. Web scrapers are highly dependent on the HTML structure of external sites; if those sites update their layout, this tool may cease to function correctly. **Use at your own risk.**

BenkyoBox is a powerful command-line utility designed for Japanese language learners and developers. It automates the process of building a local linguistic database by scraping high-quality data from several leading Japanese educational resources.

## 🚀 Features

* **Vocabulary Scraping**: Extracts Kanji, Hiragana, English meanings, and verb groups from Jisho.
* **Deep Verb Conjugation**: Automatically parses over 15+ different tenses (Plain and Polite) including Potential, Causative, Passive, and more.
* **Smart Data Mapping**: Intelligently identifies "Positive" and "Negative" forms by analyzing Japanese verb endings (`~masen`, `~nakatta`, etc.).
* **JSON Persistence**: Maintains a structured `data.json` database for offline use or integration into personal projects.
* **UTF-8 Support**: Full preservation of Japanese scripts (Kanji/Kana) and Romanized forms.

## ⚡ Powering This Project

This tool relies on the incredible data and structures provided by these community-standard resources. Please consider visiting them directly for further study:

| Source | Description |
| --- | --- |
| **[Jisho.org](https://jisho.org)** | The primary engine for dictionary data and meanings. |
| **[Japanese Verb Conjugator](https://www.japaneseverbconjugator.com/)** | The source for complex verb conjugation tables. |
| **[Japanese From Japan](https://www.japanesefromjapan.com/resources)** | Powering the Romaji conversion and resource logic. |
| **[Tofogu](https://www.google.com/search?q=https://www.tofogu.com/)** | Essential educational context and linguistic articles. |

## 🛠️ Project Structure

```text
benkyobox/
├── main.py              # CLI Entry point & Argument Parsing
├── config.py            # URL endpoints and local directory paths
├── nihongoScraper/
│   └── scraper.py       # Core logic for BeautifulSoup parsing & JSON updates
├── verbs/               # Cache directory for downloaded verb HTML pages
├── words/               # Cache directory for downloaded word HTML pages
└── data.json            # The local master database

```

## 📥 Installation

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/benkyobox.git
cd benkyobox

```


2. **Install dependencies**:
```bash
pip install beautifulsoup4 requests

```



## ⌨️ Usage

### 1. Search for General Vocabulary

To fetch a word and save its reading/meaning to your database:

```bash
python main.py sushi

```

### 2. Fetch Verb Conjugations

To scrape a verb and its full suite of complex conjugations:

```bash
python main.py tabemasu --verb

```

## 📊 Data Schema Example

Your `data.json` will be automatically updated following this structure:

```json
{
    "tabemasu": {
        "hiragana": "た",
        "kanji": "食べる",
        "meaning": "to eat",
        "group": "Ichidan verb, Transitive verb",
        "conjugations": {
            "Present Indicative": {
                "plain": { "positive": "taberu 食べる", "negative": "tabenai 食べない" },
                "polite": { "positive": "tabemasu 食べます", "negative": "tabemasen 食べません" }
            },
            "Potential": {
                "plain": { "positive": "taberareru 食べられる", "negative": "taberarenai 食べられない" },
                "polite": { "positive": "taberaremasu 食べられます", "negative": "taberaremasen 食べられません" }
            }
        }
    }
}

```

## ⚖️ License

Distributed under the MIT License. See `LICENSE` for more information.

---

*Built for the Japanese learning community.*


