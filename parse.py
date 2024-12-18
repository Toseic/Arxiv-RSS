import json
from xml.dom import minidom
from glob import glob
from pathlib import Path
from config import RSS_JSON_PATH, RAW_XML_DIR, RAW_JSON_DIR, RULE_PATH, RSS_XML_PATH
from datetime import datetime


def parse_item(item):
    title = item.getElementsByTagName("title")[0].firstChild.nodeValue
    link = item.getElementsByTagName("link")[0].firstChild.nodeValue
    description = item.getElementsByTagName("description")[0].firstChild.nodeValue
    guid = item.getElementsByTagName("guid")[0].firstChild.nodeValue
    categories = [c.firstChild.nodeValue for c in item.getElementsByTagName("category")]
    pubdate = item.getElementsByTagName("pubDate")[0].firstChild.nodeValue
    announce_type = item.getElementsByTagName("arxiv:announce_type")[
        0
    ].firstChild.nodeValue
    rights = item.getElementsByTagName("dc:rights")[0].firstChild.nodeValue
    creator = item.getElementsByTagName("dc:creator")[0].firstChild.nodeValue

    # preprocess
    description = description.split("Abstract: ")[1]

    entry = {
        "title": title,
        "link": link,
        "description": description,
        "guid": guid,
        "categories": categories,
        "pubdate": pubdate,
        "announce_type": announce_type,
        "rights": rights,
        "creator": creator,
    }

    return entry


def parse_xml() -> list[dict]:
    xml_files = glob(f"{RAW_XML_DIR}/*.xml")
    entrys = []
    for file in xml_files:
        cat_entrys = []
        with open(file, "r") as f:
            xml = minidom.parse(f)

        items = xml.getElementsByTagName("item")
        for item in items:
            try:
                entry = parse_item(item)
            except Exception as e:
                print(e)
                continue
            cat_entrys.append(entry)
            filepath = Path(file)
            with open(f"{RAW_JSON_DIR}/{filepath.stem}.json", "w") as f:
                json.dump(cat_entrys, f)
        entrys.extend(cat_entrys)

    return entrys


def load_rules():
    with open(RULE_PATH, "r") as f:
        return json.load(f)


def _filter(entry, rule):
    if isinstance(rule, str):
        if rule.startswith("%") and rule.endswith("%"):
            rule = rule[1:-1]
            return rule.lower() in (
                entry["title"] + entry["description"]
            ).lower().split(" ")
        if rule.lower() in (entry["title"] + entry["description"]).lower():
            return True
        else:
            return False
    if isinstance(rule, list):
        return any([_filter(entry, r) for r in rule])
    if isinstance(rule, dict):
        if rule["type"] == "AND":
            return all([_filter(entry, r) for r in rule["rules"]])
        elif rule["type"] == "NOT":
            return not _filter(entry, rule["rule"])

    raise ValueError(f"rule type not supported: {rule}, {type(rule)}")


def filter(entry, rules):
    """
    str: include
    list: OR
    { 'type' : 'AND' , 'rules' : [] }: AND
    { 'type' : 'NOT' , 'rule' : [] }: NOT
    """
    for rule in rules:
        if _filter(entry, rule):
            return True
    return False


def add_text_element(doc, parent, tag_name, text):
    element = doc.createElement(tag_name)
    element.appendChild(doc.createTextNode(text))
    parent.appendChild(element)


def export_rss_xml(rss_entrys):
    doc = minidom.Document()
    rss = doc.createElement("rss")
    doc.appendChild(rss)
    channel = doc.createElement("channel")
    rss.appendChild(channel)

    channel_info = {
        "title": "arxiv-rss",
        "link": "",
        "description": "",
        "docs": "",
        "language": "en-us",
        "lastBuildDate": datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z"),
        "managingEditor": "",
        "pubDate": datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z"),
    }

    for key, value in channel_info.items():
        add_text_element(doc, channel, key, value)

    for item_data in rss_entrys:
        item = doc.createElement("item")
        channel.appendChild(item)

        for key, value in item_data.items():
            if key == "categories":
                for category in value:
                    add_text_element(doc, item, "category", category)
            else:
                add_text_element(doc, item, key, value)
        channel.appendChild(item)

    fp = open(RSS_XML_PATH, "w")
    doc.writexml(fp, addindent=" ", newl="\n")

    fp.close()


def export_rss():
    rules = load_rules()
    rss_entrys = []
    entrys = parse_xml()
    for entry in entrys:
        if filter(entry, rules):
            rss_entrys.append(entry)

    with open(RSS_JSON_PATH, "w") as f:
        json.dump(rss_entrys, f)
    
    export_rss_xml(rss_entrys)
