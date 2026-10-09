"""Writes texts/<code>.json (list of chapters, each a list of verse strings) for the 73-book canon.
Bíblia Livre (CC BY 3.0 BR) for the 66 books; CPDV (public domain, English) for deuterocanonical books and Daniel 13–14."""
import csv, json, sys, os, collections
SRC, DATA, OUT = sys.argv[1:4]
data = json.load(open(DATA))
EN = {"Gen":"Genesis","Exod":"Exodus","Lev":"Leviticus","Num":"Numbers","Deut":"Deuteronomy","Josh":"Joshua","Judg":"Judges","Ruth":"Ruth","1Sam":"I Samuel","2Sam":"II Samuel","1Kgs":"I Kings","2Kgs":"II Kings","1Chr":"I Chronicles","2Chr":"II Chronicles","Ezra":"Ezra","Neh":"Nehemiah","Tob":"Tobit","Jdt":"Judith","Esth":"Esther","1Macc":"I Maccabees","2Macc":"II Maccabees","Job":"Job","Ps":"Psalms","Prov":"Proverbs","Eccl":"Ecclesiastes","Song":"Song of Solomon","Wis":"Wisdom","Sir":"Sirach","Isa":"Isaiah","Jer":"Jeremiah","Lam":"Lamentations","Bar":"Baruch","Ezek":"Ezekiel","Dan":"Daniel","Hos":"Hosea","Joel":"Joel","Amos":"Amos","Obad":"Obadiah","Jonah":"Jonah","Mic":"Micah","Nah":"Nahum","Hab":"Habakkuk","Zeph":"Zephaniah","Hag":"Haggai","Zech":"Zechariah","Mal":"Malachi","Matt":"Matthew","Mark":"Mark","Luke":"Luke","John":"John","Acts":"Acts","Rom":"Romans","1Cor":"I Corinthians","2Cor":"II Corinthians","Gal":"Galatians","Eph":"Ephesians","Phil":"Philippians","Col":"Colossians","1Thess":"I Thessalonians","2Thess":"II Thessalonians","1Tim":"I Timothy","2Tim":"II Timothy","Titus":"Titus","Phlm":"Philemon","Heb":"Hebrews","Jas":"James","1Pet":"I Peter","2Pet":"II Peter","1John":"I John","2John":"II John","3John":"III John","Jude":"Jude","Rev":"Revelation of John"}
def load(path):
    t = collections.defaultdict(lambda: collections.defaultdict(dict))
    for r in csv.DictReader(open(path, encoding="utf-8")): t[r["Book"]][int(r["Chapter"])][int(r["Verse"])] = r["Text"].strip()
    return t
pt, cp = load(f"{SRC}/formats/csv/PorBLivre.csv"), load(f"{SRC}/formats/csv/CPDV.csv")
os.makedirs(OUT, exist_ok=True); total = 0
for b in data["books"]:
    en = EN[b["code"]]; chs = []
    for c in range(1, b["n"] + 1):
        src = cp if b["deut"] or (b["code"] == "Dan" and c >= 13) else pt
        vv = src[en][c]; chs.append([vv.get(v, "") for v in range(1, (max(vv) if vv else 0) + 1)])
    s = json.dumps(chs, ensure_ascii=False, separators=(",", ":")); total += len(s.encode())
    open(f"{OUT}/{b['code']}.json", "w").write(s)
print("total bytes", total)
