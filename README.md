# 宜安路射飛鏢・今天去哪玩

從新北市中和區宜安路168巷出發，選交通方式（走路／騎車／開車）、過夜、縣市與玩的類型，射一鏢決定今天去哪玩。

- 網站：`public/index.html`（單一檔案，資料已內嵌，不需 API 金鑰）
- 資料來源：Google Places API (New)，資料日期 2026-10-16（`data/places.json`）
- 部署：推到 GitLab 預設分支後，`.gitlab-ci.yml` 的 `pages` 工作會發佈 `public/` 到 GitLab Pages
- 更新資料：`GOOGLE_PLACES_API_KEY=... python3 scripts/fetch_places.py && python3 scripts/fetch_counties.py`（金鑰只從環境變數讀取，請勿提交到 repo），再把 `data/places.json` 重新嵌入 `index.html`
