/* All cases in this file use labelled browser fixtures, not live API observations. */
const {chromium}=require('playwright');
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const {createHash}=require('node:crypto');
const ROOT=path.resolve(__dirname,'..');
(async()=>{
 const options={headless:true};
 if(process.env.VERSIONLENS_BROWSER_EXECUTABLE)options.executablePath=process.env.VERSIONLENS_BROWSER_EXECUTABLE;
 const browser=await chromium.launch(options);
 try {
 const page=await browser.newPage({viewport:{width:1440,height:1050}});
 const origin='http://127.0.0.1:8765';
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 let profile='support',currentHit,inspectOverride=null,catalogOverride=null,lastPayload;
 const upstream={chunk_id:'a'.repeat(24),version:'0.28.1',section:'Timeouts',text:'HTTPX defaults to five seconds of network inactivity.',source_id:'httpx:0.28.1:docs/quickstart.md',source_sha256:'b'.repeat(64),upstream_commit:'c'.repeat(40),source_kind:'upstream',access:'public',start_line:1,end_line:2,citation_url:'https://github.com/encode/httpx/blob/'+ 'c'.repeat(40)+'/docs/quickstart.md?plain=1#L1-L2',score:1};
 const synthetic={...upstream,source_id:'synthetic:httpx:0.28.1:incident-demo.md',section:'SYNTHETIC DEMO: Incident procedure',source_kind:'synthetic',access:'support',upstream_commit:'b'.repeat(64),citation_url:'/api/chunks/'+ 'a'.repeat(24)+'?version=0.28.1',text:'# SYNTHETIC DEMO: Incident procedure\n\nThe synthetic escalation code is orchard-42.'};
 function catalog(){return {product:'httpx',versions:['0.27.2','0.28.1'],retrievers:['keyword','vector','hybrid'],default_retriever:'keyword',access_profile:profile,permission_demo:true,index:{sources:32,chunks:644}};}
 await page.route('**/*',async route=>{
  const url=new URL(route.request().url());assert.equal(url.origin,origin);
  if(url.pathname==='/api/catalog')return route.fulfill({json:catalogOverride||catalog()});
  if(url.pathname==='/api/search'||url.pathname==='/api/ask'){
   lastPayload=route.request().postDataJSON();
   const base={question:lastPayload.question,version:lastPayload.version,retrieval_method:lastPayload.retriever};
   if(url.pathname==='/api/ask')return route.fulfill({json:{...base,status:'answered',semantic_support_verified:false,claims:[{text:'The synthetic escalation code is orchard-42.',citations:[{...currentHit,evidence_id:'E1',quote_id:'Q1',quote:'The synthetic escalation code is orchard-42.'}]}]}});
   return route.fulfill({json:{...base,status:'evidence_found',hits:[currentHit]}});
  }
  if(url.pathname.startsWith('/api/chunks/'))return route.fulfill({json:inspectOverride||currentHit});
  const name={'/':'index.html','/app.js':'app.js','/style.css':'style.css'}[url.pathname];
  if(!name)return route.fulfill({status:404,body:''});
  return route.fulfill({body:fs.readFileSync(path.join(ROOT,'src/versionlens/web',name)),contentType:{'index.html':'text/html','app.js':'text/javascript','style.css':'text/css'}[name]});
 });
 let passed=0;
 async function reload(role,hit){profile=role;currentHit=structuredClone(hit);inspectOverride=null;catalogOverride=null;await page.goto(origin);await page.waitForFunction(()=>!document.querySelector('#search-button').disabled);}
 async function search(){await page.locator('#search-button').click();await page.waitForFunction(()=>!document.querySelector('#search-button').disabled);}
 await reload('public',upstream);await search();assert.equal(await page.locator('.evidence-card').count(),1);assert.equal(await page.locator('#access-profile').textContent(),'Public demo access');assert.match(await page.locator('.source-kind').textContent(),/Official HTTPX source/);passed++;
 await reload('support',synthetic);await search();assert.equal(await page.locator('.evidence-card').count(),1);assert.match(await page.locator('.synthetic-notice').textContent(),/SYNTHETIC DEMO.*not official/);assert.equal(await page.locator('.source-link').getAttribute('href'),origin+synthetic.citation_url);assert.deepEqual(Object.keys(lastPayload).sort(),['limit','question','retriever','version']);passed++;
 await page.locator('.evidence-card summary').click();await page.getByRole('button',{name:'Inspect source chunk'}).click();await page.locator('#source-dialog .source-text').waitFor();assert.match(await page.locator('#source-dialog').textContent(),/Revision SHA/);assert.equal(await page.locator('#source-dialog .source-text').textContent(),synthetic.text);await page.keyboard.press('Escape');passed++;
 await page.locator('#ask-button').click();await page.locator('.draft-claim').waitFor();assert.match(await page.locator('.claim-citations').textContent(),/synthetic demo/);assert.equal(await page.locator('#result-body .synthetic-notice').count(),1);passed++;
 await reload('public',synthetic);await search();assert.equal(await page.locator('.evidence-card').count(),0);assert.equal(await page.locator('#result-body a').count(),0);assert.match(await page.locator('#request-status').getAttribute('class'),/is-error/);passed++;
 await reload('public',{...synthetic,access:'public'});await search();assert.equal(await page.locator('.evidence-card').count(),1);passed++;
 const bads=[{source_kind:'unknown'},{source_kind:undefined},{access:'admin'},{access:undefined},{upstream_commit:'d'.repeat(64)},{source_id:'synthetic:httpx:0.28.1:../demo.md'},{citation_url:'https://evil.invalid/'+synthetic.citation_url},{citation_url:origin+synthetic.citation_url},{citation_url:synthetic.citation_url+'&role=support'},{citation_url:'/api/chunks/'+ 'd'.repeat(24)+'?version=0.28.1'},{citation_url:synthetic.citation_url.replace('0.28.1','0.27.2')}];
 for(const changed of bads){await reload('support',{...synthetic,...changed});await search();assert.equal(await page.locator('.evidence-card').count(),0);assert.equal(await page.locator('#result-body a').count(),0);passed++;}
 await reload('support',{...synthetic,text:synthetic.text+'\n<img src=x onerror="window.uiXss=true">'});await search();assert.equal(await page.locator('#result-body img').count(),0);assert.equal(await page.evaluate(()=>window.uiXss),undefined);assert.match(await page.locator('#result-body').textContent(),/<img src=x/);passed++;
 await page.setViewportSize({width:360,height:900});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));passed++;
 await reload('support',synthetic);await search();await page.locator('.evidence-card summary').click();inspectOverride={...synthetic,access:'public'};await page.getByRole('button',{name:'Inspect source chunk'}).click();await page.locator('#source-dialog .field-error').waitFor();assert.equal(await page.locator('#source-dialog .source-text').count(),0);passed++;
 for(const changed of [{access_profile:'admin'},{permission_demo:false},{access_profile:undefined}]){catalogOverride={...catalog(),...changed};await page.goto(origin);await page.locator('#catalog-error').waitFor({state:'visible'});assert.equal(await page.locator('#search-button').isDisabled(),true);passed++;}
 assert.deepEqual(errors,[]);
 const report={kind:'isolated_browser_fixtures',recorded_at_utc:new Date().toISOString(),browser:browser.version(),passed,failed:0,page_errors:errors,screenshots:false,
 implementation_sha256:Object.fromEntries(['src/versionlens/web/app.js','src/versionlens/web/index.html','src/versionlens/web/style.css','scripts/check_permission_fixtures.cjs'].map(name=>[name,createHash('sha256').update(fs.readFileSync(path.join(ROOT,name))).digest('hex')])),
 limitations:'Every API response is a browser fixture. This checks client consistency guards, not backend access or real model behavior.'};
 const output=path.resolve(ROOT,process.env.VERSIONLENS_FIXTURE_REPORT||'reports/local/day5-permission-fixtures.json');
 fs.mkdirSync(path.dirname(output),{recursive:true});fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({kind:report.kind,passed,failed:0}));
 } finally {await browser.close();}
})().catch(e=>{console.error(e.stack);process.exit(1);});
