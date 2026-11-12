#!/usr/bin/env python3
"""Republish approved Taken Faceclaims from the existing Apps Script JSONP feed.

The existing feed decides what is public. This script never reads a spreadsheet,
never asks for credentials, and deliberately rejects unexpected feed schemas.
"""
import json
import os
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

FEED_URL = os.environ.get('KH_FEED_URL', '').strip()
if not FEED_URL.startswith('https://script.google.com/macros/s/') or '/exec' not in FEED_URL:
    raise SystemExit('Set repository Actions variable KH_FEED_URL to the deployed Apps Script /exec URL.')

parts = urlsplit(FEED_URL)
params = [(k, v) for k, v in parse_qsl(parts.query) if k != 'feed']
params.append(('feed', 'takenfcs'))
url = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(params), ''))

req = Request(url, headers={'User-Agent':'KismetHarbor-Static-Publisher/1.0', 'Accept':'text/javascript'})
with urlopen(req, timeout=45) as response:
    text = response.read(2_000_000).decode('utf-8-sig').strip()

prefix = 'window.khTakenFcReceive('
if not text.startswith(prefix) or not text.endswith(');'):
    raise SystemExit('Apps Script did not return the expected public Taken FC feed. Check deployment permissions and URL.')

payload = json.loads(text[len(prefix):-2])
if payload.get('version') != 1 or not isinstance(payload.get('characters'), list) or not isinstance(payload.get('theme'), dict):
    raise SystemExit('Unexpected feed structure; refusing to publish.')

# Public-only contract: no sensitive spreadsheet columns can slip into the static file.
allowed_person = {'faceclaim', 'name', 'id', 'status'}
allowed_theme = {'rust','rose','cream','maroon','italic','link','paper','ink','line'}
valid_status = {'active', 'retired', 'deceased'}
people = []
for raw in payload['characters']:
    if not isinstance(raw, dict):
        raise SystemExit('Bad character record; refusing to publish.')
    if str(raw.get('status','')).strip().lower() not in valid_status:
        raise SystemExit('A non-public character status was encountered; refusing to publish.')
    if not str(raw.get('name','')).strip() or not str(raw.get('faceclaim','')).strip():
        raise SystemExit('Missing name/faceclaim; refusing to publish.')
    people.append({k: str(raw.get(k,'') or '') for k in ('faceclaim','name','id','status')})

result = {
    'version': 1,
    'generated': str(payload.get('generated','')),
    'theme': {k: str(v) for k,v in payload['theme'].items() if k in allowed_theme},
    'characters': people,
}
out = Path('docs/takenfcs.json')
out.parent.mkdir(parents=True, exist_ok=True)
serialized = json.dumps(result, indent=2, ensure_ascii=False) + '\n'
if not out.exists() or out.read_text(encoding='utf-8') != serialized:
    out.write_text(serialized, encoding='utf-8')
print(f'Validated and exported {len(people)} public faceclaims to {out}')
