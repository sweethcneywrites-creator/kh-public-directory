#!/usr/bin/env python3
"""Publish public OOC profiles and activity sessions without copying admin-only columns."""s
import json
import os
from pathlib import Path
from urllib.parse import urlsplit, parse_qsl, urlencode, urlunsplit
from urllib.request import Request, urlopen

base = os.environ.get('KH_FEED_URL', '').strip()
if not base.startswith('https://script.google.com/macros/s/') or '/exec' not in base:
    raise SystemExit('KH_FEED_URL must point to the public Apps Script /exec URL')

def get_feed(which, callback):
    parts = urlsplit(base)
    q = [(k, v) for k, v in parse_qsl(parts.query) if k != 'feed'] + [('feed', which)]
    url = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(q), ''))
    req = Request(url, headers={'User-Agent': 'KismetHarbor-Static-Publisher/2.1'})
    with urlopen(req, timeout=90) as response:
        text = response.read(5_000_000).decode('utf-8-sig').strip()
    prefix = 'window.' + callback + '('
    if not text.startswith(prefix) or not text.endswith(');'):
        raise SystemExit('Unexpected response for feed=' + which + '; deploy the updated Apps Script /exec version')
    return json.loads(text[len(prefix):-2])

def save(name, obj):
    path = Path('docs') / (name + '.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    print('Published', path, path.stat().st_size, 'bytes')

directory = get_feed('directory', 'khDirectoryBundleReceive')
if directory.get('version') != 2:
    raise SystemExit('Unexpected directory bundle version')
writers = directory.get('writers')
if not isinstance(writers, list):
    raise SystemExit('Directory feed missing public writers')
for writer in writers:
    if not isinstance(writer, dict) or set(writer) - {'alias', 'pronouns', 'timezone', 'age', 'role', 'count', 'characters'}:
        raise SystemExit('Unexpected public writer field')
    if not isinstance(writer.get('characters'), list):
        raise SystemExit('Invalid writer roster')
    for item in writer['characters']:
        if not isinstance(item, dict) or set(item) - {'name', 'faceclaim'}:
            raise SystemExit('Unexpected writer roster field')
theme = directory.get('theme')
if not isinstance(theme, dict) or set(theme) - {'rust', 'rose', 'cream', 'maroon', 'italic', 'link', 'paper', 'ink', 'line'}:
    raise SystemExit('Invalid theme')
save('ooc', {'version': 2, 'generated': directory.get('generated'), 'theme': theme, 'writers': writers})

calendar = get_feed('calendar', 'khCalendarFeedReceive')
if calendar.get('version') != 1:
    raise SystemExit('Unexpected calendar feed version')
activities = calendar.get('activities')
sessions = calendar.get('sessions')
if not isinstance(activities, list) or not isinstance(sessions, list):
    raise SystemExit('Calendar sections absent')
allow_a = {'Activity ID', 'Activity Name', 'Location', 'Season'}
allow_s = {'Activity ID', 'Activity Name', 'Meeting pattern (source text)', 'Location', 'Season'}
for collection, allowed in ((activities, allow_a), (sessions, allow_s)):
    for item in collection:
        if not isinstance(item, dict) or set(item) - allowed:
            raise SystemExit('Nonpublic calendar field received; refusing to publish')
save('calendar', {'version': 1, 'generated': calendar.get('generated'), 'theme': theme, 'activities': activities, 'sessions': sessions})
