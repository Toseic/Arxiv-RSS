from pathlib import Path

DATA_PATH = Path("./data").resolve()


ALL_CATS_PATH = DATA_PATH / "json" / "cats" / "all_cats.json" # choose your rss categories from here
RSS_CATS_PATH = DATA_PATH / "json" / "cats" / "rss_cats.json"

RAW_XML_DIR = DATA_PATH / "xml" 
RAW_JSON_DIR = DATA_PATH / "json" / "raw" 
RSS_JSON_PATH = DATA_PATH / "rss" / "rss.json" 
RSS_XML_PATH = DATA_PATH / "rss" / "rss.xml" 

RULE_PATH = DATA_PATH / "json" / "rules" / "rules.json"