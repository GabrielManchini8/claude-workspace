"""Builds atlas.json (people, places, journeys, per-chapter mentions) from Theographic Bible Metadata.

Usage: python3 prep_atlas.py <theographic clone> <data.json from prep.py> <names_pt.json> <land.json> <out.json>
"""
import csv, json, sys, collections

TH, DATA, NAMES, LAND, OUT = sys.argv[1:6]
data = json.load(open(DATA))
names = json.load(open(NAMES))
books = data["books"]
code_idx = {b["code"]: i for i, b in enumerate(books)}

def ch_index(code, c):
    b = books[code_idx[code]]
    return b["start"] + c - 1

rd = lambda f: list(csv.DictReader(open(f"{TH}/CSV/{f}.csv", encoding="utf-8-sig")))
P, L, V = rd("People"), rd("Places"), rd("Verses")

for k in names["people"]:
    if k not in {r["personLookup"] for r in P}: print("unknown person", k)
for k in names["places"]:
    if k not in {r["placeLookup"] for r in L}: print("unknown place", k)

SKIP_PLACES = {"holy_place_575", "most_holy_place_827", "river_244", "river_1010"}
SKIP_PEOPLE = {"god_1324", "holy_spirit_7400"}

# lugares deuterocanônicos que não existem na base (KJV): coordenadas aproximadas
EXTRA_PLACES = [
    ("rages_x", "Rages", 35.59, 51.44, "City"),
    ("modin_x", "Modin", 31.93, 35.03, "City"),
]

places, pidx = [], {}
for r in L:
    if not r["latitude"] or not r["longitude"] or r["placeLookup"] in SKIP_PLACES: continue
    vc = int(r["verseCount"] or 0)
    if vc == 0: continue
    pidx[r["placeLookup"]] = len(places)
    places.append([names["places"].get(r["placeLookup"], r["displayTitle"]), round(float(r["latitude"]), 4),
                   round(float(r["longitude"]), 4), r["featureType"][:1] or "?", vc])
for k, n, la, lo, t in EXTRA_PLACES:
    pidx[k] = len(places); places.append([n, la, lo, t[:1], 0])

people, hidx = [], {}
for r in P:
    if r["personLookup"] in SKIP_PEOPLE: continue
    hidx[r["personLookup"]] = len(people)
    people.append(r)

def ids(s, m):
    return [m[x] for x in s.split(",") if x and x in m] if s else []

import re
EN2PT = {}
name_count = collections.Counter(r["name"] for r in P)
for r in P:
    k = r["personLookup"]
    if k in names["people"] and name_count[r["name"]] == 1:
        EN2PT.setdefault(r["name"], re.sub(r" \(.*\)$", "", names["people"][k]))
REL = [("father of", "pai de"), ("mother of", "mãe de"), ("son of", "filho de"), ("daughter of", "filha de"),
       ("brother of", "irmão de"), ("sister of", "irmã de"), ("wife of", "esposa de"), ("husband of", "marido de"),
       ("grandson of", "neto de"), ("King of", "rei de"), ("king of", "rei de"), ("descendant of", "descendente de"),
       ("Brother of", "irmão de"), ("Son of", "filho de"), ("Mother of", "mãe de"), ("Wife of", "esposa de"), ("Husband of", "marido de"), ("High Priest", "sumo sacerdote"), ("Disciple at", "discípulo em")]
def pt_name(r):
    k = r["personLookup"]
    if k in names["people"]: return names["people"][k]
    n = r["displayTitle"]
    m = re.match(r"^(.*?) \((.*)\)$", n)
    base = EN2PT.get(r["name"], m.group(1) if m else n)
    if not m: return base
    d = m.group(2)
    for a, b in REL: d = d.replace(a, b)
    d = re.sub(r"[A-Z][a-z]+", lambda w: EN2PT.get(w.group(0), w.group(0)), d)
    return f"{base} ({d})"

people_out = []
for r in people:
    people_out.append([
        pt_name(r),
        (r["gender"] or "?")[:1],
        hidx.get(r["father"], -1), hidx.get(r["mother"], -1),
        ids(r["children"], hidx), ids(r["partners"], hidx), int(r["verseCount"] or 0),
    ])

# menções por capítulo e coocorrência pessoa-lugar no mesmo versículo
ch_people = collections.defaultdict(collections.Counter)
ch_places = collections.defaultdict(collections.Counter)
co = collections.defaultdict(collections.Counter)
miss = 0
for r in V:
    code, c, _ = r["osisRef"].split(".")
    if code not in code_idx: miss += 1; continue
    i = ch_index(code, int(c))
    ps = [hidx[x] for x in r["people"].split(",") if x in hidx] if r["people"] else []
    ls = [pidx[x] for x in r["places"].split(",") if x in pidx] if r["places"] else []
    for p in ps: ch_people[i][p] += 1
    for l in ls: ch_places[i][l] += 1
    for p in ps:
        for l in ls: co[p][l] += 1

N = len(data["chapters"])
chP = [[x for kv in ch_people[i].most_common(40) for x in kv] for i in range(N)]
chL = [[x for kv in ch_places[i].most_common(40) for x in kv] for i in range(N)]
coOut = {str(p): [x for kv in c.most_common(30) for x in kv] for p, c in co.items()}

# viagens curadas: (rótulo, cor, [(lugar, referência, código do livro, capítulo)])
J = [
 ("Abraão", "Gn 11–25", [("ur_1189","Gn 11,31","Gen",11),("haran_527","Gn 11,31","Gen",11),("shechem_1069","Gn 12,6","Gen",12),("bethel_202","Gn 12,8","Gen",12),("egypt_362","Gn 12,10","Gen",12),("bethel_202","Gn 13,3","Gen",13),("hebron_551","Gn 13,18","Gen",13),("beersheba_170","Gn 21,31","Gen",21),("moriah_821","Gn 22,2","Gen",22),("machpelah_748","Gn 25,9","Gen",25)]),
 ("Jacó", "Gn 28–46", [("beersheba_170","Gn 28,10","Gen",28),("bethel_202","Gn 28,19","Gen",28),("paddan-aram_916","Gn 28,5","Gen",28),("mahanaim_756","Gn 32,2","Gen",32),("penuel_931","Gn 32,31","Gen",32),("succoth_1113","Gn 33,17","Gen",33),("shechem_1069","Gn 33,18","Gen",33),("bethel_202","Gn 35,6","Gen",35),("ephrath_403","Gn 35,19","Gen",35),("hebron_551","Gn 35,27","Gen",35),("egypt_362","Gn 46,6","Gen",46)]),
 ("Êxodo", "Ex 12 – Js 6", [("rameses_980","Ex 12,37","Exod",12),("succoth_1114","Ex 12,37","Exod",12),("etham_417","Ex 13,20","Exod",13),("pi-hahiroth_948","Ex 14,2","Exod",14),("marah_765","Ex 15,23","Exod",15),("elim_369","Ex 15,27","Exod",15),("sin_1097","Ex 16,1","Exod",16),("rephidim_996","Ex 17,1","Exod",17),("mount_sinai_855","Ex 19,1","Exod",19),("kadesh-barnea_663","Nm 13,26","Num",13),("mount_hor_842","Nm 20,22","Num",20),("mount_nebo_849","Dt 34,1","Deut",34),("jericho_634","Js 6","Josh",6)]),
 ("Davi", "1Sm 16 – 2Sm 5", [("bethlehem_218","1Sm 16,4","1Sam",16),("valley_of_elah_1201","1Sm 17,2","1Sam",17),("gibeah_466","1Sm 18,2","1Sam",18),("adullam_31","1Sm 22,1","1Sam",22),("ziklag_1259","1Sm 27,6","1Sam",27),("hebron_551","2Sm 2,1-4","2Sam",2),("jerusalem_636","2Sm 5,6-7","2Sam",5)]),
 ("Elias", "1Rs 17 – 2Rs 2", [("tishbe_1171","1Rs 17,1","1Kgs",17),("cherith_286","1Rs 17,3","1Kgs",17),("zarephath_1242","1Rs 17,9","1Kgs",17),("carmel_278","1Rs 18,19","1Kgs",18),("jezreel_643","1Rs 18,45","1Kgs",18),("beersheba_170","1Rs 19,3","1Kgs",19),("horeb_576","1Rs 19,8","1Kgs",19),("jericho_634","2Rs 2,4","2Kgs",2),("jordan_653","2Rs 2,7-11","2Kgs",2)]),
 ("Exílio e retorno", "2Rs 25 – Ne 2", [("jerusalem_636","2Rs 25,1","2Kgs",25),("riblah_1001","2Rs 25,6","2Kgs",25),("babylon_151","2Rs 25,7","2Kgs",25),("susa_1118","Ne 1,1","Neh",1),("jerusalem_636","Ne 2,11","Neh",2)]),
 ("Tobias", "Tb 5–11 (deuterocanônico)", [("nineveh_899","Tb 5,1","Tob",5),("ecbatana_353","Tb 7,1","Tob",7),("rages_x","Tb 9,2","Tob",9),("ecbatana_353","Tb 9,5","Tob",9),("nineveh_899","Tb 11,1","Tob",11)]),
 ("Macabeus", "1Mc 2–4 (deuterocanônico)", [("jerusalem_636","1Mc 1,20","1Macc",1),("modin_x","1Mc 2,1","1Macc",2),("emmaus_382","1Mc 3,40","1Macc",3),("beth-zur_242","1Mc 4,29","1Macc",4),("jerusalem_636","1Mc 4,36","1Macc",4)]),
 ("Jesus", "Mt, Lc, Jo", [("bethlehem_218","Lc 2,4-7","Luke",2),("egypt_362","Mt 2,14","Matt",2),("nazareth_878","Mt 2,23","Matt",2),("bethany_187","Jo 1,28","John",1),("cana_271","Jo 2,1","John",2),("capernaum_274","Mt 4,13","Matt",4),("tyre_1184","Mc 7,24","Mark",7),("caesarea_philippi_267","Mt 16,13","Matt",16),("jericho_634","Lc 19,1","Luke",19),("bethany_186","Jo 12,1","John",12),("jerusalem_636","Mt 21,10","Matt",21),("emmaus_382","Lc 24,13","Luke",24),("mount_of_olives_861","At 1,12","Acts",1)]),
]
journeys = []
for label, refs, steps in J:
    st = []
    for lk, ref, code, c in steps:
        if lk not in pidx: print("journey place missing", lk); continue
        st.append([pidx[lk], ref, ch_index(code, c)])
    journeys.append({"n": label, "r": refs, "s": st})

# viagens de Paulo (geojson do Theographic)
g = json.load(open(f"{TH}/geo/pauls_journeys_all.geojson"))
routes = collections.defaultdict(list)
for f in g["features"]:
    if f["geometry"]["type"] != "LineString": continue
    pts, last = [], None
    for lo, la in f["geometry"]["coordinates"]:
        if last is None or abs(lo - last[0]) + abs(la - last[1]) > 0.05:
            pts += [round(lo, 3), round(la, 3)]; last = (lo, la)
    pts += [round(f["geometry"]["coordinates"][-1][0], 3), round(f["geometry"]["coordinates"][-1][1], 3)]
    routes[f["properties"]["route_id"]].append(pts)
paul = [{"n": n, "r": r, "lines": routes[k], "ch": ch_index("Acts", c)} for k, n, r, c in
        [(1, "Paulo · 1ª viagem", "At 13–14", 13), (2, "Paulo · 2ª viagem", "At 15,36 – 18,22", 16), (3, "Paulo · 3ª viagem", "At 18,23 – 21,17", 19), (4, "Paulo · viagem a Roma", "At 27–28", 27)]]

# linha de Jesus a Adão pelos pais (genealogia de Mateus + Gênesis)
byid = {r["personLookup"]: r for r in P}
line, cur = [], "jesus_905"
while cur in hidx and len(line) < 100:
    line.append(hidx[cur]); cur = byid[cur]["father"]

out = {"places": places, "people": people_out, "chP": chP, "chL": chL, "co": coOut,
       "journeys": journeys, "paul": paul, "line": line, "land": json.load(open(LAND)),
       "special": {"jesus": hidx["jesus_905"], "joseph": hidx["joseph_1715"], "mary": hidx["mary_1938"]}}
json.dump(out, open(OUT, "w"), separators=(",", ":"), ensure_ascii=False)
print(len(places), "places;", len(people_out), "people;", len(line), "generations; verses outside canon map:", miss)
