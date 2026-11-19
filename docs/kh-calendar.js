/* Kismet Harbor • isolated, GitHub-hosted Community Activities Calendar.
   Does not depend on kh-directory.js. Data: docs/calendar.json. */
(function () {
  'use strict';
  const script = document.currentScript;
  const mount = document.getElementById('kh-static-directory');
  if (!mount) return;
  const base = 'https://sweethcneywrites-creator.github.io/kh-public-directory/';
  const root = document.createElement('div');
  root.id = 'kh-community-calendar';
  mount.replaceChildren(root);
  const shadow = root.attachShadow({mode:'open'});
  const style = document.createElement('style');
  style.textContent = `@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Karla:wght@400;500;600;700&display=swap');
  :host {display:block;--rust:#b8572a;--rose:#c28c80;--cream:#f5e6d3;--maroon:#8b3a3a;--ink:#392b29;--paper:#fcf8f3;--line:#e5d4c7;font:15px/1.55 Karla,Arial,sans-serif;color:var(--ink);background:var(--paper)}
  *{box-sizing:border-box}a{color:var(--maroon)}
  .hero{background:var(--rose);padding:30px max(20px,calc((100% - 1240px)/2)) 37px;border-bottom:1px solid var(--line)}
  .eyebrow{font-size:11px;font-weight:800;letter-spacing:.18em;text-transform:uppercase;color:var(--maroon)}
  h1,h2,h3{font-family:'DM Serif Display',Georgia,serif;font-weight:400}h1{font-size:clamp(39px,5vw,67px);line-height:1.08;text-transform:lowercase;margin:8px 0 12px}p{margin:7px 0}
  .hero p{max-width:780px;font-size:15px}.wrap{max-width:1240px;margin:auto;padding:22px 24px 70px}
  .intro{display:flex;flex-wrap:wrap;gap:10px;justify-content:space-between;align-items:baseline}.intro a{font-weight:700}
  .jump{display:flex;gap:8px;flex-wrap:wrap;margin:20px 0 30px}.jump button{cursor:pointer;font:700 12px Karla,Arial,sans-serif;border:1px solid var(--line);background:var(--cream);color:var(--maroon);border-radius:5px;padding:10px 13px}.jump button:hover,.jump button:focus-visible{background:var(--maroon);color:#fff}
  .day{margin:26px 0 41px;scroll-margin-top:20px}.day h2{font-size:35px;color:var(--maroon);border-bottom:1px solid var(--rust);padding-bottom:9px;margin:0 0 17px}
  .count{font:600 12px Karla,Arial,sans-serif;color:var(--maroon);margin-left:11px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:13px}
  .entry{background:#fffaf6;border:1px solid var(--rose);border-top:3px solid var(--rust);border-radius:9px;padding:16px;min-width:0}.entry h3{font-size:24px;color:var(--maroon);margin:4px 0 8px}.time{font-weight:800;color:var(--rust)}.meta{font-size:13px;line-height:1.5;margin:5px 0}.arrange{padding:20px;background:var(--cream);border-radius:12px}.muted{color:#86695e;font-size:13px}.error{padding:23px;border:1px solid var(--rust);background:#fffaf6}
  @media(max-width:680px){.hero{padding:26px 17px 30px}.wrap{padding:18px 15px 45px}.grid{grid-template-columns:1fr}h1{font-size:43px}.day h2{font-size:30px}}
  @media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}`;
  shadow.append(style);
  const shell = document.createElement('div');
  shell.innerHTML = '<section class="hero"><div class="eyebrow">COMMUNITY / WEEKLY SCHEDULE</div><h1>the community calendar.</h1><p>Recurring meetings, clubs, and gatherings around Kismet Harbor.</p></section><main class="wrap"><div class="intro"><p>Browse by weekday or find flexible groups under By Arrangement.</p><a href="https://kismetharbor.tumblr.com/activities">Explore activities</a></div><div id="calendar-content"><p>Loading community activity sessions…</p></div></main>';
  shadow.append(shell);
  const content = shadow.getElementById('calendar-content');
  const days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function time(text){
    const s=String(text||'');
    const range=s.match(/\b\d{1,2}\s*(?:[:.]\d\d)?\s*[–-]\s*\d{1,2}(?::\d\d)?\s*(?:AM|PM)\b/i);
    if(range)return range[0].replace(/\s+/g,' ').toUpperCase();
    const one=s.match(/\b\d{1,2}(?::\d\d)?\s*(?:AM|PM)\b/i);
    if(one)return one[0].replace(/\s+/g,' ').toUpperCase();
    if(/\bdawn\b/i.test(s))return 'Dawn';if(/after sunset/i.test(s))return 'After sunset';
    if(/\bnoon\b/i.test(s))return '12 PM';if(/early morning/i.test(s))return 'Early morning';return 'TBD';
  }
  function interpret(pattern,name){
    const s=String(pattern||'').trim(),low=s.toLowerCase();
    if(/equine emporium/i.test(name)||/saturday or sunday/i.test(low))return [{day:'arrangement',time:'TBD',frequency:'Twice monthly · Saturday or Sunday',note:'Members arrange the weekend day and time'}];
    if(/first day of the month|first of the month|^on the first of the month/.test(low))return [{day:'arrangement',time:time(s),frequency:'First day of each month',note:'Calendar date varies by weekday'}];
    if(/^aa\s*&\s*na$/i.test(name)&&/aa\s*\d/i.test(low)&&/na\s*\d/i.test(low)){
      const aa=s.match(/AA\s*(\d{1,2}(?::\d\d)?\s*(?:AM|PM))/i),na=s.match(/NA\s*(\d{1,2}(?::\d\d)?\s*(?:AM|PM))/i);
      if(aa&&na)return [{day:'Wednesday',time:aa[1].toUpperCase(),frequency:'Every week',suffix:' — AA'},{day:'Wednesday',time:na[1].toUpperCase(),frequency:'Every week',suffix:' — NA'}];
    }
    let parts=s.split(/\s*;\s*/);
    if(/\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)s?\b[^/]*\/[^/]*\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)s?\b/i.test(s))parts=s.split(/\s*\/\s*/);
    const out=[];
    for(const part of parts){
      const t=part.toLowerCase();const ds=days.filter(d=>new RegExp('\\b'+d.toLowerCase()+'s?\\b').test(t));
      for(const d of ds){
        let freq='Every week';const m=t.match(/\b(first|second|third|fourth|last)\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)/);
        if(m)freq=m[1][0].toUpperCase()+m[1].slice(1)+' '+d+' monthly';
        else if(/biweekly|every other/.test(t))freq='Every other week';
        else if(/once per month|monthly/.test(t))freq='Once monthly';
        out.push({day:d,time:time(part),frequency:freq});
      }
    }
    return out.length?out:[{day:'arrangement',time:time(s),frequency:s||'Schedule arranged by members'}];
  }
  function timeOrder(text){const m=String(text).match(/(\d{1,2})(?::(\d\d))?\s*(AM|PM)/i);return m?(Number(m[1])%12+(m[3].toUpperCase()==='PM'?12:0))*60+Number(m[2]||0):9999;}
  function card(e){return '<article class="entry"><div class="time">'+esc(e.time)+'</div><h3>'+esc(e.name)+'</h3><p class="meta">'+esc(e.frequency)+'</p><p class="meta">'+esc(e.location)+'</p>'+(e.season&&!/^not specified$/i.test(e.season)?'<p class="meta"><em>'+esc(e.season)+'</em></p>':'')+(e.note?'<p class="meta">'+esc(e.note)+'</p>':'')+(e.day==='arrangement'?'<p class="meta muted">'+esc(e.pattern)+'</p>':'')+'</article>';}
  function applyTheme(theme){
    if(!theme || typeof theme!=='object')return;
    for(const key of ['rust','rose','cream','maroon','ink','paper','line']){
      const val=String(theme[key]||'');if(/^#[0-9a-f]{6}$/i.test(val))root.style.setProperty('--'+key,val);
    }
  }
  function render(data){
    if(!data || !Array.isArray(data.activities) || !Array.isArray(data.sessions))throw Error('Calendar data is missing activities or sessions.');
    applyTheme(data.theme);
    const activities=new Map(data.activities.map(a=>[String(a['Activity ID']||'').trim().toUpperCase(),a]));
    const entries=[];
    for(const s of data.sessions){
      const a=activities.get(String(s['Activity ID']||'').trim().toUpperCase())||{};
      const name=a['Activity Name']||s['Activity Name'];if(!name)continue;
      const pattern=s['Meeting pattern (source text)']||'';
      for(const p of interpret(pattern,name))entries.push({...p,name:name+(p.suffix||''),pattern,location:s.Location||a.Location||'Location to be confirmed',season:s.Season||a.Season||''});
    }
    if(!entries.length){content.innerHTML='<div class="error"><strong>No activity sessions were published.</strong><p>GitHub loaded calendar.json, but no matching session records were found. Check the ACTIVITY SESSIONS sheet and the calendar publishing feed; this is not the birthdays page.</p></div>';return;}
    const nav='<div class="jump">'+days.map(d=>'<button type="button" data-target="day-'+d.toLowerCase()+'">'+d+'</button>').join('')+'<button type="button" data-target="by-arrangement">By Arrangement</button></div>';
    function section(day,label){const group=entries.filter(e=>e.day===day).sort((a,b)=>timeOrder(a.time)-timeOrder(b.time)||a.name.localeCompare(b.name));return '<section class="day'+(day==='arrangement'?' arrange':'')+'" id="'+(day==='arrangement'?'by-arrangement':'day-'+day.toLowerCase())+'"><h2>'+label+' <span class="count">'+group.length+' '+(group.length===1?'activity':'activities')+'</span></h2>'+(group.length?'<div class="grid">'+group.map(card).join('')+'</div>':'<p class="muted">No fixed meetings currently listed.</p>')+'</section>';}
    content.innerHTML=nav+days.map(d=>section(d,d)).join('')+section('arrangement','By Arrangement');
    content.querySelectorAll('[data-target]').forEach(btn=>btn.addEventListener('click',()=>{
      const dest=shadow.getElementById(btn.dataset.target);if(!dest)return;
      const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
      dest.scrollIntoView({behavior:reduce?'auto':'smooth',block:'start'});
    }));
  }
  fetch(base+'calendar.json',{cache:'no-cache'})
    .then(r=>{if(!r.ok)throw Error('GitHub calendar.json returned HTTP '+r.status);return r.json();})
    .then(render)
    .catch(err=>{content.innerHTML='<div class="error"><strong>Community calendar could not load.</strong><p>'+esc(err.message||err)+'</p></div>';});
})();
