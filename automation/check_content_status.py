"""Observe dates without generating or re-dating any content."""
import datetime as dt
import json
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
TZ=ZoneInfo("Asia/Shanghai")

def inspect(job, data, now):
    expected=now.date().isoformat()
    if job["cadence"]=="monthly":
        expected=now.strftime("%Y-%m")
        dates=[x.get("month","") for x in data.get("issues",[])]
    elif job["kind"]=="entries":
        dates=[x.get("date","") for x in data.get("entries",[])]
    else:
        stamp=data.get("updated_at")
        dates=[dt.datetime.fromisoformat(stamp.replace("Z","+00:00")).astimezone(TZ).date().isoformat()] if stamp else []
        if job["cadence"]=="weekly":
            expected=(now.date()-dt.timedelta(days=now.weekday())).isoformat()
            dates=[(dt.date.fromisoformat(d)-dt.timedelta(days=dt.date.fromisoformat(d).weekday())).isoformat() for d in dates]
    return {"state":"current" if expected in dates else "stale","last_content_at":max(dates,default=None),
            "expected_period":expected,"error":None}

def main():
    now=dt.datetime.now(TZ)
    jobs=json.loads((ROOT/"automation/content-jobs.json").read_text())
    report={"attempted_at":now.isoformat(),"engine":"chatgpt-scheduled-task","columns":{}}
    for job in jobs:
        try:
            data=json.loads((ROOT/"data"/(job["id"]+".json")).read_text())
            report["columns"][job["id"]]=inspect(job,data,now)
        except Exception as error:
            report["columns"][job["id"]]={"state":"failed","error":"内容文件读取或格式错误："+type(error).__name__}
    (ROOT/"data/update-status.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print("Current columns:",sum(c["state"]=="current" for c in report["columns"].values()),"/",len(jobs))

if __name__=="__main__":
    main()
