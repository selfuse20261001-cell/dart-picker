import os,json,urllib.request,concurrent.futures as cf
K=os.environ["GOOGLE_PLACES_API_KEY"]
d=json.load(open("data/places.json"))
def get(pid):
    r=urllib.request.Request(f"https://places.googleapis.com/v1/places/{pid}?languageCode=zh-TW&regionCode=TW",headers={"X-Goog-Api-Key":K,"X-Goog-FieldMask":"reviewSummary,editorialSummary,reviews"})
    for t in range(3):
        try: return json.load(urllib.request.urlopen(r,timeout=20))
        except Exception as e: err=str(e)
    return {"_err":err}
def trunc(s,n=42):
    s=" ".join(s.split());return s if len(s)<=n else s[:n]+"…"
with cf.ThreadPoolExecutor(8) as ex: res=list(ex.map(get,[p["place_id"] for p in d["places"]]))
c={"gemini":0,"editorial":0,"reviews":0,"none":0,"err":0}
for p,j in zip(d["places"],res):
    if "_err" in j: c["err"]+=1
    rs=j.get("reviewSummary",{}); ed=j.get("editorialSummary",{})
    if rs.get("text",{}).get("text"):
        p["rv"]={"type":"gemini","text":rs["text"]["text"],"disclosure":(rs.get("disclosureText") or {}).get("text","由 Gemini 摘要"),"uri":rs.get("reviewsUri") or rs.get("flagContentUri")};c["gemini"]+=1
    elif ed.get("text"):
        p["rv"]={"type":"editorial","text":ed["text"]};c["editorial"]+=1
    elif j.get("reviews"):
        q=[]
        for r in j["reviews"][:6]:
            t=(r.get("text") or r.get("originalText") or {}).get("text")
            if t and len(q)<3: q.append({"q":trunc(t),"a":r.get("authorAttribution",{}).get("displayName",""),"au":r.get("authorAttribution",{}).get("uri",""),"r":r.get("rating"),"t":r.get("relativePublishTimeDescription","")})
        if q: p["rv"]={"type":"reviews","quotes":q};c["reviews"]+=1
        else: c["none"]+=1
    else: c["none"]+=1
json.dump(d,open("data/places.json","w"),ensure_ascii=False)
print(c)
