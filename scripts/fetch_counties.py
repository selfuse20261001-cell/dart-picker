import os,json,math,urllib.request,re,collections
K=os.environ["GOOGLE_PLACES_API_KEY"]
M="places.id,places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.googleMapsUri,places.types"
def post(body):
    r=urllib.request.Request("https://places.googleapis.com/v1/places:searchText",json.dumps(body).encode(),{"Content-Type":"application/json","X-Goog-Api-Key":K,"X-Goog-FieldMask":M})
    try: return json.load(urllib.request.urlopen(r)).get("places",[])
    except Exception as e: print("err",e); return []
d=json.load(open("data/places.json"));O=(d["origin"]["lat"],d["origin"]["lng"])
def km(b):
    a=O;x=math.sin(math.radians(b[0]-a[0])/2)**2+math.cos(math.radians(a[0]))*math.cos(math.radians(b[0]))*math.sin(math.radians(b[1]-a[1])/2)**2
    return 2*6371*math.asin(math.sqrt(x))
C={"基隆市":(25.13,121.74,12),"臺北市":(25.06,121.55,15),"新北市":(25.0,121.6,40),"桃園市":(24.9,121.25,30),"新竹市":(24.8,120.97,10),"新竹縣":(24.7,121.15,35),"苗栗縣":(24.5,120.9,40),"臺中市":(24.2,120.8,45),"南投縣":(23.85,120.95,50),"宜蘭縣":(24.65,121.65,40)}
ALIAS={"台北市":"臺北市","台中市":"臺中市"}
QS=[("公園/自然步道","步道 森林遊樂區 風景區",0),("夜市美食","夜市",0),("景點古蹟","老街 古蹟 景點",0),("室內/親子","博物館 主題樂園 親子",0),("溫泉/露營","溫泉",1),("溫泉/露營","露營區",1),("溫泉/露營","休閒農場 民宿",1),("購物","購物中心 outlet",0)]
def county(addr):
    for a,b in ALIAS.items(): addr=addr.replace(a,b)
    for c in C:
        if c in addr and not (c=="新竹市" and "新竹縣" in addr): return c
    return None
places={p["place_id"]:p for p in d["places"]}
for p in places.values(): p["county"]=county(p["addr"]) or "新北市"
for c,(la,ln,r) in ([] if os.environ.get("EXTRA_ONLY") else C.items()):
    for cat,q,night in QS:
        for p in post({"textQuery":f"{c} {q}","languageCode":"zh-TW","maxResultCount":10,"locationBias":{"circle":{"center":{"latitude":la,"longitude":ln},"radius":r*1000.0}}}):
            if p["id"] in places: continue
            cc=county(p.get("formattedAddress",""))
            if cc!=c: continue
            ll=(p["location"]["latitude"],p["location"]["longitude"]);dist=km(ll)
            rc=p.get("userRatingCount") or 0
            if rc<(200 if dist>15 else 30): continue
            t=p.get("types",[])
            n=bool(night or dist>60 or any(x in t for x in["lodging","campground","resort_hotel","hotel","farmstay","rv_park"]))
            places[p["id"]]=dict(name=p["displayName"]["text"],cat=cat,night=n,lat=ll[0],lng=ll[1],addr=p.get("formattedAddress",""),rating=p.get("rating"),reviews=rc,url=p.get("googleMapsUri"),place_id=p["id"],km=round(dist,2),src="Places API",note="",county=cc)
EX=[("南投縣","日月潭","景點古蹟",1),("南投縣","日月潭 飯店","溫泉/露營",1),("南投縣","清境農場","公園/自然步道",1),("南投縣","清境 民宿","溫泉/露營",1),("南投縣","溪頭","公園/自然步道",1),("宜蘭縣","礁溪溫泉","溫泉/露營",1),("苗栗縣","南庄","景點古蹟",1),("新竹縣","尖石 露營","溫泉/露營",1),("臺中市","武陵農場","公園/自然步道",1)]
for c,q,cat,night in EX:
    la,ln,r=C[c]
    for p in post({"textQuery":q,"languageCode":"zh-TW","maxResultCount":10,"locationBias":{"circle":{"center":{"latitude":la,"longitude":ln},"radius":r*1000.0}}}):
        if p["id"] in places or county(p.get("formattedAddress","")) is None: continue
        ll=(p["location"]["latitude"],p["location"]["longitude"]);rc=p.get("userRatingCount") or 0
        if rc<200: continue
        places[p["id"]]=dict(name=p["displayName"]["text"],cat=cat,night=True,lat=ll[0],lng=ll[1],addr=p.get("formattedAddress",""),rating=p.get("rating"),reviews=rc,url=p.get("googleMapsUri"),place_id=p["id"],km=round(km(ll),2),src="Places API",note="",county=county(p["formattedAddress"]))
for p in places.values():
    if p["km"]>60: p["night"]=True
d["places"]=list(places.values());json.dump(d,open("data/places.json","w"),ensure_ascii=False)
P=d["places"];print(len(P),collections.Counter(p["county"] for p in P))
print(collections.Counter("walk" if p["km"]<=1.5 else "ride" if p["km"]<=8 else "drive" for p in P),"night",sum(p["night"] for p in P),"max km",max(p["km"] for p in P))
for k in["清境","日月潭","南庄","尖石","礁溪"]: print(k,sum(k in p["name"]+p["addr"] for p in P))
