import copy
import datetime as dt
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('updater',ROOT/'automation/update_content.py')
u=importlib.util.module_from_spec(spec)
spec.loader.exec_module(u)
JOBS=u.read(ROOT/'automation/content-jobs.json')
NOW=dt.datetime(2026,10,26,9,tzinfo=u.TZ)

class ContentTests(unittest.TestCase):
    def test_week_and_month_boundaries(self):
        weekly=next(j for j in JOBS if j['id']=='software-weekly')
        self.assertEqual(u.period(weekly,NOW),'2026-10-26')
        self.assertFalse(u.is_current(weekly,{'updated_at':'2026-10-25T23:59:00+08:00'},NOW))
        self.assertTrue(u.is_current(weekly,{'updated_at':'2026-10-26T01:00:00+08:00'},NOW))
        monthly=next(j for j in JOBS if j['kind']=='issues')
        self.assertTrue(u.is_current(monthly,{'issues':[{'month':'2026-10'}]},NOW))
        self.assertFalse(u.is_current(monthly,{'issues':[{'month':'2026-09'}]},NOW))

    def test_merge_preserves_history_and_deduplicates_day(self):
        job=next(j for j in JOBS if j['kind']=='entries')
        old={'entries':[{'date':'2026-10-25','title':'old'},{'date':'2026-10-26','title':'retry'}]}
        result=u.merge(job,old,{'date':'wrong','title':'new'},NOW)
        self.assertEqual([e['title'] for e in result['entries']],['old','new'])
        self.assertEqual(result['entries'][1]['date'],'2026-10-26')
        self.assertEqual(old['entries'][1]['title'],'retry')

    def test_rejects_unknown_source_and_repeated_article(self):
        job=next(j for j in JOBS if j['id']=='daily-knowledge')
        value=copy.deepcopy(job['sample'])
        value['title']='new theme'
        urls=u.urls_in(value)
        u.validate(job,value,urls,{'entries':[]})
        with self.assertRaises(ValueError):u.validate(job,value,set(),{'entries':[]})
        with self.assertRaises(ValueError):u.validate(job,value,urls,{'entries':[value]})

    def test_news_rejects_empty_and_wrong_count(self):
        job=next(j for j in JOBS if j['id']=='daily-news')
        value=copy.deepcopy(job['sample'])
        value['updated_at']='2026-10-26T09:00:00+08:00'
        value['stories']=value['stories'][:6]
        with self.assertRaises(ValueError):u.validate(job,value,set(),{})

    def test_missing_key_preserves_original_and_reports_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            (root/'automation').mkdir();(root/'data').mkdir()
            job=next(j for j in JOBS if j['id']=='daily-knowledge')
            u.write(root/'automation/content-jobs.json',[job])
            sample=copy.deepcopy(job['sample'])
            sample['date']='2000-01-01'
            original={'entries':[sample]}
            u.write(root/'data/daily-knowledge.json',original)
            with patch.object(u,'ROOT',root),patch.dict(u.os.environ,{'AUTO_CONTENT_ENABLED':'true','OPENAI_API_KEY':''}),patch('sys.argv',['updater']):
                self.assertEqual(u.main(),1)
            self.assertEqual(u.read(root/'data/daily-knowledge.json'),original)
            self.assertEqual(u.read(root/'data/update-status.json')['columns']['daily-knowledge']['state'],'failed')

if __name__=='__main__':unittest.main()
