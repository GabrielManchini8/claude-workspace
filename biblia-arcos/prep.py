import csv, json, sys, collections

SRC = sys.argv[1]  # repo dir
OUT = sys.argv[2]

# Catholic canon order (CIC 120). code (OpenBible), Portuguese name, abbrev, KJV/CPDV name, deutero?
BOOKS = [
 ("Gen","Gênesis","Gn","Genesis",0),("Exod","Êxodo","Ex","Exodus",0),("Lev","Levítico","Lv","Leviticus",0),
 ("Num","Números","Nm","Numbers",0),("Deut","Deuteronômio","Dt","Deuteronomy",0),("Josh","Josué","Js","Joshua",0),
 ("Judg","Juízes","Jz","Judges",0),("Ruth","Rute","Rt","Ruth",0),("1Sam","1 Samuel","1Sm","I Samuel",0),
 ("2Sam","2 Samuel","2Sm","II Samuel",0),("1Kgs","1 Reis","1Rs","I Kings",0),("2Kgs","2 Reis","2Rs","II Kings",0),
 ("1Chr","1 Crônicas","1Cr","I Chronicles",0),("2Chr","2 Crônicas","2Cr","II Chronicles",0),("Ezra","Esdras","Esd","Ezra",0),
 ("Neh","Neemias","Ne","Nehemiah",0),("Tob","Tobias","Tb","Tobit",1),("Jdt","Judite","Jt","Judith",1),
 ("Esth","Ester","Est","Esther",0),("1Macc","1 Macabeus","1Mc","I Maccabees",1),("2Macc","2 Macabeus","2Mc","II Maccabees",1),
 ("Job","Jó","Jó","Job",0),("Ps","Salmos","Sl","Psalms",0),("Prov","Provérbios","Pr","Proverbs",0),
 ("Eccl","Eclesiastes","Ecl","Ecclesiastes",0),("Song","Cântico dos Cânticos","Ct","Song of Solomon",0),
 ("Wis","Sabedoria","Sb","Wisdom",1),("Sir","Eclesiástico (Sirácida)","Eclo","Sirach",1),
 ("Isa","Isaías","Is","Isaiah",0),("Jer","Jeremias","Jr","Jeremiah",0),("Lam","Lamentações","Lm","Lamentations",0),
 ("Bar","Baruc","Br","Baruch",1),("Ezek","Ezequiel","Ez","Ezekiel",0),("Dan","Daniel","Dn","Daniel",0),
 ("Hos","Oseias","Os","Hosea",0),("Joel","Joel","Jl","Joel",0),("Amos","Amós","Am","Amos",0),("Obad","Abdias","Ab","Obadiah",0),
 ("Jonah","Jonas","Jn","Jonah",0),("Mic","Miqueias","Mq","Micah",0),("Nah","Naum","Na","Nahum",0),
 ("Hab","Habacuc","Hab","Habakkuk",0),("Zeph","Sofonias","Sf","Zephaniah",0),("Hag","Ageu","Ag","Haggai",0),
 ("Zech","Zacarias","Zc","Zechariah",0),("Mal","Malaquias","Ml","Malachi",0),
 ("Matt","Mateus","Mt","Matthew",0),("Mark","Marcos","Mc","Mark",0),("Luke","Lucas","Lc","Luke",0),("John","João","Jo","John",0),
 ("Acts","Atos","At","Acts",0),("Rom","Romanos","Rm","Romans",0),("1Cor","1 Coríntios","1Cor","I Corinthians",0),
 ("2Cor","2 Coríntios","2Cor","II Corinthians",0),("Gal","Gálatas","Gl","Galatians",0),("Eph","Efésios","Ef","Ephesians",0),
 ("Phil","Filipenses","Fl","Philippians",0),("Col","Colossenses","Cl","Colossians",0),("1Thess","1 Tessalonicenses","1Ts","I Thessalonians",0),
 ("2Thess","2 Tessalonicenses","2Ts","II Thessalonians",0),("1Tim","1 Timóteo","1Tm","I Timothy",0),("2Tim","2 Timóteo","2Tm","II Timothy",0),
 ("Titus","Tito","Tt","Titus",0),("Phlm","Filêmon","Fm","Philemon",0),("Heb","Hebreus","Hb","Hebrews",0),("Jas","Tiago","Tg","James",0),
 ("1Pet","1 Pedro","1Pd","I Peter",0),("2Pet","2 Pedro","2Pd","II Peter",0),("1John","1 João","1Jo","I John",0),
 ("2John","2 João","2Jo","II John",0),("3John","3 João","3Jo","III John",0),("Jude","Judas","Jd","Jude",0),("Rev","Apocalipse","Ap","Revelation of John",0),
]
assert len(BOOKS) == 73

def verse_counts(path):
    vc = collections.defaultdict(lambda: collections.defaultdict(int))
    for r in csv.DictReader(open(path, encoding="utf-8")):
        vc[r["Book"]][int(r["Chapter"])] += 1
    return vc

kjv = verse_counts(f"{SRC}/formats/csv/KJV.csv")
cpdv = verse_counts(f"{SRC}/formats/csv/CPDV.csv")

chapters = []   # [bookIndex, chapterNumber, verses, deuteroFlag]
index = {}
books_out = []
for bi, (code, pt, ab, en, deut) in enumerate(BOOKS):
    if deut:
        src = cpdv[en]
        nch = max(src)
    elif code == "Dan":
        src = None
        nch = 14   # Daniel 13 (Susana) e 14 (Bel e o Dragão) são deuterocanônicos
    else:
        src = kjv[en]
        nch = max(src)
    start = len(chapters)
    for c in range(1, nch + 1):
        if code == "Dan":
            v = kjv[en][c] if c <= 12 else cpdv[en][c]
            d = 1 if c >= 13 else 0
        else:
            v = src[c]
            d = deut
        index[(code, c)] = len(chapters)
        chapters.append([bi, c, v, d])
    books_out.append({"code": code, "pt": pt, "ab": ab, "deut": deut, "start": start, "n": nch})

# Aggregate OpenBible verse refs into chapter pairs
pairs = {}
total = 0
skipped = 0
with open(f"{SRC}/sources/extras/cross_references.txt", encoding="utf-8") as f:
    next(f)
    for line in f:
        a, b, v = line.rstrip("\n").split("\t")
        v = int(v)
        total += 1
        ab_, ac = a.split(".")[0], int(a.split(".")[1])
        bs = b.split("-")[0].split(".")
        bb, bc = bs[0], int(bs[1])
        if (ab_, ac) not in index or (bb, bc) not in index:
            skipped += 1
            continue
        i, j = index[(ab_, ac)], index[(bb, bc)]
        if i == j:
            continue
        k = (min(i, j), max(i, j))
        p = pairs.get(k)
        if p is None:
            pairs[k] = [1, v]
        else:
            p[0] += 1
            if v > p[1]:
                p[1] = v

# flat arrays: i, j, count, maxVotes
flat = []
for (i, j), (c, mv) in sorted(pairs.items(), key=lambda kv: kv[1][1]):
    flat += [i, j, c, max(mv, 0)]

data = {"books": books_out, "chapters": chapters, "pairs": flat,
        "stats": {"verseRefs": total, "skipped": skipped, "chapterPairs": len(pairs)}}
json.dump(data, open(OUT, "w"), separators=(",", ":"), ensure_ascii=False)
print(len(chapters), "chapters;", len(pairs), "chapter pairs;", total, "verse refs; skipped", skipped)
