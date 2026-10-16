import os,json,math,urllib.request
K=os.environ["GOOGLE_PLACES_API_KEY"]
def post(url,body,mask):
    r=urllib.request.Request(url,json.dumps(body).encode(),{"Content-Type":"application/json","X-Goog-Api-Key":K,"X-Goog-FieldMask":mask})
    return json.load(urllib.request.urlopen(r))
M="places.id,places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.googleMapsUri,places.types"
g=post("https://places.googleapis.com/v1/places:searchText",{"textQuery":"新北市中和區宜安路168巷","languageCode":"zh-TW"},M)["places"][0]
O=(g["location"]["latitude"],g["location"]["longitude"])
def km(a,b):
    x=math.sin(math.radians(b[0]-a[0])/2)**2+math.cos(math.radians(a[0]))*math.cos(math.radians(b[0]))*math.sin(math.radians(b[1]-a[1])/2)**2
    return 2*6371*math.asin(math.sqrt(x))
Q=[("walk",1500,[("公園/自然步道","公園",0),("夜市美食","夜市 小吃",0),("景點古蹟","廟宇 景點",0),("室內/親子","親子 室內 圖書館",0),("購物","購物中心 商圈",0)]),
   ("ride",8000,[("公園/自然步道","河濱公園 步道",0),("夜市美食","夜市",0),("景點古蹟","景點 古蹟",0),("室內/親子","博物館 親子館",0),("購物","百貨公司 老街",0)]),
   ("drive",40000,[("公園/自然步道","國家森林遊樂區 步道",0),("溫泉/露營","溫泉 飯店",1),("溫泉/露營","露營區",1),("景點古蹟","老街 景點 民宿",1),("室內/親子","主題樂園 水族館",0),("夜市美食","觀光夜市",0)])]
out={};
for mode,rad,qs in Q:
    for cat,q,night in qs:
        res=post("https://places.googleapis.com/v1/places:searchText",{"textQuery":q,"languageCode":"zh-TW","maxResultCount":8 if mode!="walk" else 6,
            "locationBias":{"circle":{"center":{"latitude":O[0],"longitude":O[1]},"radius":min(rad,50000.0)}}},M).get("places",[])
        for p in res:
            ll=(p["location"]["latitude"],p["location"]["longitude"]);d=km(O,ll)
            if d>rad/1000 or p["id"] in out or (p.get("userRatingCount") or 0)<30: continue
            t=p.get("types",[]);n=night or any(x in t for x in["lodging","campground","resort_hotel","hotel"]) or d>25
            out[p["id"]]=dict(name=p["displayName"]["text"],cat=cat,night=bool(n),lat=ll[0],lng=ll[1],addr=p.get("formattedAddress",""),rating=p.get("rating"),reviews=p.get("userRatingCount"),url=p.get("googleMapsUri"),place_id=p["id"],km=round(d,2),src="Places API",note="")
json.dump({"origin":{"lat":O[0],"lng":O[1],"addr":g.get("formattedAddress")},"places":list(out.values())},open("data/places.json","w"),ensure_ascii=False)
import collections;print(O,len(out),collections.Counter(("walk" if p["km"]<=1.5 else "ride" if p["km"]<=8 else "drive") for p in out.values()),sum(p["night"] for p in out.values()))
