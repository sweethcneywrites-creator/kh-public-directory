#!/usr/bin/env python3
"""Publish validated public-facing Kismet Harbor pages from the Apps Script public feed."""
import json, os, re
from pathlib import Path
from urllib.parse import urlsplit, parse_qsl, urlencode, urlunsplit
from urllib.request import Request, urlopen

base=os.environ.get('KH_FEED_URL','').strip()
if not base.startswith('https://script.google.com/macros/s/') or '/exec' not in base:
    raise SystemExit('KH_FEED_URL must be the public Apps Script /exec URL')
p=urlsplit(base)
query=[(k,v) for k,v in parse_qsl(p.query) if k!='feed']+[('feed','directory')]
url=urlunsplit((p.scheme,p.netloc,p.path,urlencode(query),''))
req=Request(url,headers={'User-Agent':'KismetHarbor-Static-Publisher/2.0','Accept':'text/javascript'})
with urlopen(req,timeout=90) as response:
    response_text=response.read(5_000_000).decode('utf-8-sig').strip()
prefix='window.khDirectoryBundleReceive('
if not response_text.startswith(prefix) or not response_text.endswith(');'):
    raise SystemExit('Unexpected response; make sure updated Code.gs is deployed as a new /exec version')
data=json.loads(response_text[len(prefix):-2])
if data.get('version')!=2:raise SystemExit('Unexpected bundle version')
# Fail closed if the backend accidentally starts including new or private columns.
whitelist={
 'characters':{'Character ID','Name','Full Name','Status','Published','Faceclaim','Date of Birth','Pronouns','Neighborhood','Occupation (for jobs NOT listed on locations page)','Time in Kismet Harbor','Custom Blurb','__rich_Custom Blurb','Blog URL','Introduction URL','Portrait URL'},
 'npcs':{'Name / Group','Status','Category','Description','NPC ID'},
 'locations':{'Location ID','Name','Status','Neighborhood','Location','Year Opened','Owner Slots','Photo URL','Description','__rich_Description','Rental / Services','staff','hires'},
 'activities':{'Activity ID','Activity Name','Category','Schedule Display','Location','Season','Description'},
 'members':{'Activity ID','Character ID','NPC ID','person','Role'},
 'alumni':{'School','Graduation Year','Character Name','Character ID','NPC ID','Status','derivedStatus','Degree / Major'},
 'relationships':{'Section','Category','Relationship Text','Open Slots'},
 'living':{'Neighborhood','Property Section','Building / Property','Residents','Residence Details','Availability','Open Roommate Slots'},
 'wanted':{'Category','Status','Connection Title','Wanted By','Filled By','Tumblr Post URL'},
 'anniversaries':{'Month','Day','Year','Custom Event Name'},
 'birthdays':{'Name','Status','Date of Birth','Character ID','NPC ID'}
}
allowed_status={'active','retired','deceased'}
for typ,fields in whitelist.items():
    rows=data.get(typ)
    if not isinstance(rows,list):raise SystemExit('Invalid or missing data section: '+typ)
    for row in rows:
        if not isinstance(row,dict) or set(row)-fields:
            raise SystemExit('Non-approved field in '+typ+'; refusing to publish')
        if typ=='characters' and (str(row.get('Status','')).lower() not in allowed_status or str(row.get('Published','')).lower()=='unpublished'):
            raise SystemExit('Found non-public character: refusing to publish')
        if typ=='locations':
            if not isinstance(row.get('staff',[]),list) or not isinstance(row.get('hires',[]),list):raise SystemExit('Invalid location staffing')
            for staff in row['staff']:
                if set(staff)-{'Position Type','Display Order','Role / Job Title','person','Location ID'}:raise SystemExit('Unexpected staff field')
if not isinstance(data.get('statusByName'),dict): raise SystemExit('Missing public badge names')
allowed_theme={'rust','rose','cream','maroon','italic','link','paper','ink','line'}
if not isinstance(data.get('theme'),dict) or set(data['theme'])-allowed_theme:raise SystemExit('Unexpected theme keys')
shared={k:data[k] for k in ('version','generated','theme')}
# Only the supporting records each page needs, never the whole bundle on individual page visits.
def pagefile(name,keys):
    obj=dict(shared)
    for k in keys:obj[k]=data[k]
    path=Path('docs')/(name+'.json');path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    print(name, len(path.read_bytes()),'bytes')
pagefile('characters',['characters'])
pagefile('retired',['characters'])
pagefile('npcs',['npcs'])
pagefile('locations',['locations','statusByName'])
pagefile('activities',['activities','members','statusByName'])
pagefile('alumni',['alumni'])
pagefile('relationships',['relationships','statusByName'])
pagefile('living',['living','statusByName'])
pagefile('wanted',['wanted','statusByName'])
pagefile('anniversaries',['anniversaries','birthdays'])
