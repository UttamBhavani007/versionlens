/* Real local HTTP/browser checks. No routes or API responses are mocked. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {createHash}=require('node:crypto');
const {chromium}=require('playwright');
const ROOT=path.resolve(__dirname,'..');
const PUBLIC=process.env.VERSIONLENS_PUBLIC_URL||'http://127.0.0.1:8765';
const SUPPORT=process.env.VERSIONLENS_SUPPORT_URL||'http://127.0.0.1:8766';
for(const value of [PUBLIC,SUPPORT]){const url=new URL(value);assert.equal(url.protocol,'http:');assert.equal(url.hostname,'127.0.0.1');assert.equal(url.username+url.password+url.search+url.hash,'');assert.equal(url.pathname,'/');}
const OUTPUT=path.resolve(ROOT,process.env.VERSIONLENS_ACCESS_REPORT||'reports/local/day5-access-browser.json');
const IMAGES=path.join(ROOT,'docs/screenshots');
const checks=[],screenshots=[],observations=[],external=[],errors=[];
async function main(){
 const options={headless:true};if(process.env.VERSIONLENS_BROWSER_EXECUTABLE)options.executablePath=process.env.VERSIONLENS_BROWSER_EXECUTABLE;
 const browser=await chromium.launch(options);
 const page=await browser.newPage({viewport:{width:1440,height:1050}});
 page.on('pageerror',error=>errors.push(error.message));
 await page.route('**/*',route=>{if(![new URL(PUBLIC).origin,new URL(SUPPORT).origin].includes(new URL(route.request().url()).origin)){external.push(route.request().url());return route.abort();}return route.continue();});
 let failure,restricted;
 async function check(name,fn){await fn();checks.push({name,status:'passed'});console.log(JSON.stringify({check:name,status:'passed'}));}
 async function ready(url){await page.goto(url);await page.waitForFunction(()=>!document.querySelector('#search-button').disabled);}
 async function action(button,endpoint){const pending=page.waitForResponse(r=>new URL(r.url()).pathname===endpoint&&r.request().method()==='POST',{timeout:150000});await page.locator(button).click();const response=await pending;assert.equal(response.status(),200);const result=await response.json();await page.waitForFunction(()=>!document.querySelector('#search-button').disabled);return result;}
 async function capture(filename){await page.screenshot({path:path.join(IMAGES,filename),fullPage:false});screenshots.push(filename);}
 try{
  fs.mkdirSync(IMAGES,{recursive:true});
  await check('public catalog contains only accessible counts',async()=>{await ready(PUBLIC);assert.equal(await page.locator('#access-profile').textContent(),'Public demo access');assert.match(await page.locator('#corpus-count').textContent(),/32 source files.*644 indexed excerpts/);});
  await check('real public question abstains without generation',async()=>{await page.locator('#question').fill('orchidrelay');const result=await action('#ask-button','/api/ask');assert.equal(result.status,'abstained');assert.equal(result.model_called,false);assert.equal(await page.locator('.evidence-card').count(),0);await page.locator('h1').click();await capture('day5-public-abstention.png');observations.push({case_id:'public_answer',result});});
  await check('support profile retrieves labelled synthetic evidence',async()=>{await ready(SUPPORT);assert.equal(await page.locator('#access-profile').textContent(),'Support demo access');assert.match(await page.locator('#corpus-count').textContent(),/34 source files.*646 indexed excerpts/);await page.locator('#question').fill('orchidrelay');const result=await action('#search-button','/api/search');restricted=result.hits[0];assert.equal(restricted.source_kind,'synthetic');assert.equal(restricted.access,'support');assert.match(restricted.text,/3 attempts/);assert.match(await page.locator('.synthetic-notice').first().textContent(),/not official HTTPX guidance/);await page.locator('h1').click();await capture('day5-support-evidence.png');});
  await check('protected source inspector uses digest provenance',async()=>{await page.locator('.evidence-card summary').first().click();await page.getByRole('button',{name:'Inspect source chunk'}).first().click();await page.locator('#source-dialog .source-text').waitFor();assert.equal(await page.locator('#source-dialog .source-text').textContent(),restricted.text);assert.match(await page.locator('#source-dialog').textContent(),/Revision SHA/);await capture('day5-synthetic-inspector.png');await page.keyboard.press('Escape');});
  await check('real HTTP rejects self-promotion and hides known source IDs',async()=>{await ready(PUBLIC);const results=await page.evaluate(async id=>{const promoted=await fetch('/api/search',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:'orchidrelay',version:'0.28.1',access_profile:'support'})});const known=await fetch(`/api/chunks/${id}?version=0.28.1`);const unknown=await fetch('/api/chunks/000000000000000000000000?version=0.28.1');return {promotion:promoted.status,known:{status:known.status,body:await known.json()},unknown:{status:unknown.status,body:await unknown.json()}};},restricted.chunk_id);assert.equal(results.promotion,400);assert.equal(results.known.status,404);assert.deepEqual(results.known,results.unknown);observations.push({case_id:'http_access_controls',result:results});});
  await check('version switch shows the older fictional value only',async()=>{await ready(SUPPORT);await page.locator('#question').fill('orchidrelay');await page.locator('#version').selectOption('0.27.2');const result=await action('#search-button','/api/search');assert(result.hits.every(hit=>hit.version==='0.27.2'));assert.match(result.hits[0].text,/2 attempts/);assert.notEqual(result.hits[0].chunk_id,restricted.chunk_id);});
  await check('real synthetic draft keeps warning and exact quotations',async()=>{await page.locator('#version').selectOption('0.28.1');const result=await action('#ask-button','/api/ask');assert(['answered','abstained'].includes(result.status));assert.equal(result.semantic_support_verified,false);observations.push({case_id:'synthetic_draft',result});if(result.status==='answered'){assert.equal(result.citation_identity_and_quotes_checked,true);assert(result.claims.every(claim=>claim.citations.every(cite=>cite.source_kind==='synthetic'&&cite.version==='0.28.1')));assert.match(await page.locator('.draft-notice').textContent(),/check the cited sources/);await page.locator('h1').click();await capture('day5-synthetic-draft.png');}});
  await check('mobile synthetic workspace has no horizontal overflow',async()=>{await page.setViewportSize({width:360,height:900});await page.locator('#search-button').click();await page.locator('.evidence-card').first().waitFor();assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.locator('.results').evaluate(el=>el.scrollIntoView({block:'start'}));await capture('day5-mobile-synthetic.png');});
  assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
 }catch(error){failure=error.message;}
 finally{
  const names=[...fs.readdirSync(path.join(ROOT,'src/versionlens')).filter(name=>name.endsWith('.py')).map(name=>'src/versionlens/'+name),'src/versionlens/web/app.js','src/versionlens/web/index.html','src/versionlens/web/style.css','scripts/check_access_web.cjs'];
  const report={kind:'real_local_access_browser_checks',recorded_at_utc:new Date().toISOString(),browser:browser.version(),status:failure?'failed':'passed',checks,observations,screenshots,page_errors:errors,external_requests:external,implementation_sha256:Object.fromEntries(names.map(name=>[name,createHash('sha256').update(fs.readFileSync(path.join(ROOT,name))).digest('hex')])),limitations:['Real HTTP responses and local model; no API fixtures in this script.','Synthetic facts and startup profiles simulate access; this is not production authentication.','Generated observations do not establish general answer accuracy or semantic entailment.']};
  if(failure)report.error=failure;fs.mkdirSync(path.dirname(OUTPUT),{recursive:true});fs.writeFileSync(OUTPUT,JSON.stringify(report,null,2)+'\n');await browser.close();
 }
 if(failure)throw new Error(failure);
}
main().catch(error=>{console.error(error.message);process.exitCode=1;});
