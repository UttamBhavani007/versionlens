/* Optional browser verification. Application runtime has no Node dependency. */
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const {createHash} = require("node:crypto");
const path = require("node:path");
const {chromium} = require("playwright");

const ROOT = path.resolve(__dirname, "..");
const ORIGIN = process.env.VERSIONLENS_WEB_URL || "http://127.0.0.1:8765";
const origin = new URL(ORIGIN);
assert.equal(origin.protocol, "http:");
assert.equal(origin.hostname, "127.0.0.1");
assert.equal(origin.username + origin.password + origin.search + origin.hash, "");
const OUTPUT = path.resolve(ROOT, process.env.VERSIONLENS_BROWSER_REPORT || "reports/local/day4-browser.json");
const IMAGES = path.join(ROOT, "docs/screenshots");
const checks = [];
const externalRequests = [];
const pageErrors = [];
const screenshots = [];

async function check(name, fn) {
  await fn();
  checks.push({name, status:"passed"});
  console.log(JSON.stringify({check:name, status:"passed"}));
}

async function main() {
  fs.mkdirSync(IMAGES, {recursive:true});
  const options = {headless:true};
  if (process.env.VERSIONLENS_BROWSER_EXECUTABLE) options.executablePath = process.env.VERSIONLENS_BROWSER_EXECUTABLE;
  const browser = await chromium.launch(options);
  const page = await browser.newPage({viewport:{width:1440,height:1050}, deviceScaleFactor:1});
  page.on("pageerror", error=>pageErrors.push(error.message));
  await page.route("**/*", route=>{
    if (new URL(route.request().url()).origin !== origin.origin) {
      externalRequests.push(route.request().url());
      return route.abort();
    }
    return route.continue();
  });
  let failure;
  let evidence;
  try {
    await check("catalog and default selection", async()=>{
      await page.goto(ORIGIN);
      await page.locator("#search-button").waitFor({state:"visible"});
      await page.waitForFunction(()=>!document.querySelector("#search-button").disabled);
      assert.equal(await page.locator("#version").inputValue(), "0.28.1");
      assert.equal(await page.locator("#retriever").inputValue(), "keyword");
      assert.match(await page.locator("#corpus-count").textContent(), /32 source files.*644 indexed excerpts/);
    });
    await check("real keyword evidence and immutable links", async()=>{
      const response=page.waitForResponse(r=>r.url()===origin.origin+"/api/search" && r.request().method()==="POST");
      await page.locator("#search-button").click();
      evidence=await (await response).json();
      await page.locator(".evidence-card").first().waitFor();
      assert.equal(evidence.hits.length,5);
      assert(evidence.hits.every(hit=>hit.version==="0.28.1"));
      const links=await page.locator(".evidence-card a").evaluateAll(items=>items.map(item=>({href:item.href,rel:item.rel})));
      assert(links.every(item=>item.href.startsWith("https://github.com/encode/httpx/blob/") && item.rel.includes("noopener")));
      const filename="day4-desktop-evidence.png";
      await page.screenshot({path:path.join(IMAGES,filename),fullPage:false});
      screenshots.push(filename);
    });
    await check("source inspector matches returned excerpt",async()=>{
      await page.locator("h1").click();
      await page.locator(".evidence-card details").first().locator("summary").click();
      await page.getByRole("button",{name:"Inspect source chunk"}).first().click();
      await page.locator("#source-dialog .source-text").waitFor();
      assert.equal(await page.locator("#source-dialog .source-text").textContent(),evidence.hits[0].text);
      assert((await page.locator("#source-body").textContent()).includes(evidence.hits[0].source_sha256));
      const filename="day4-source-inspector.png";
      await page.screenshot({path:path.join(IMAGES,filename),fullPage:false});
      screenshots.push(filename);
      await page.keyboard.press("Escape");
      assert.equal(await page.locator("#source-dialog").evaluate(el=>el.open),false);
    });
    await check("version change invalidates prior evidence",async()=>{
      await page.locator("#version").selectOption("0.27.2");
      assert.equal(await page.locator(".evidence-card").count(),0);
      await page.locator("#search-button").click();
      await page.locator(".evidence-card").first().waitFor();
      const badges=await page.locator(".evidence-card .version-badge").allTextContents();
      assert(badges.length && badges.every(value=>value==="HTTPX 0.27.2"));
    });
    await check("real missing-evidence abstention without generation",async()=>{
      await page.locator("#version").selectOption("0.28.1");
      await page.getByRole("button",{name:"Missing evidence",exact:true}).click();
      const response=page.waitForResponse(r=>r.url()===origin.origin+"/api/ask");
      await page.locator("#ask-button").click();
      const result=await (await response).json();
      assert.equal(result.status,"abstained");
      assert.equal(result.model_called,false);
      await page.waitForFunction(()=>document.querySelector("#request-status").textContent.includes("service abstained"));
      assert.match(await page.locator("#result-body").textContent(),/generation model was not called/i);
    });
    if(process.env.VERSIONLENS_CHECK_GENERATION === "1") {
      await check("real cited draft retains warnings and source quotes",async()=>{
        await page.getByRole("button",{name:"Default timeout",exact:true}).click();
        const response=page.waitForResponse(r=>r.url()===origin.origin+"/api/ask",{timeout:150000});
        await page.locator("#ask-button").click();
        const result=await (await response).json();
        assert.equal(result.status,"answered");
        assert.equal(result.semantic_support_verified,false);
        assert.equal(result.citation_identity_and_quotes_checked,true);
        await page.locator(".draft-claim").first().waitFor();
        assert.match(await page.locator(".draft-notice").textContent(),/check the cited sources/);
        const quotes=await page.locator(".citation-quote").allTextContents();
        assert.deepEqual(quotes,result.claims.flatMap(claim=>claim.citations.map(citation=>citation.quote)));
        await page.locator("h1").click();
        const filename="day4-cited-draft.png";
        await page.screenshot({path:path.join(IMAGES,filename),fullPage:false});
        screenshots.push(filename);
      });
    }
    await check("empty-question validation and focus",async()=>{
      await page.locator("#question").fill("");
      await page.locator("#search-button").click();
      assert.equal(await page.locator("#question").getAttribute("aria-invalid"),"true");
      assert.equal(await page.locator("#question").evaluate(el=>el===document.activeElement),true);
      assert.equal(await page.locator("#question-error").isVisible(),true);
    });
    // These next checks are labelled browser fixtures, not live model observations.
    await check("fixture: stale response cannot cross a version change",async()=>{
      let release;
      const barrier=new Promise(resolve=>{release=resolve;});
      let arrived;
      const arrival=new Promise(resolve=>{arrived=resolve;});
      await page.route("**/api/search",async route=>{arrived();await barrier;await route.fulfill({json:evidence}).catch(()=>{});});
      await page.locator("#question").fill(evidence.question);
      await page.locator("#search-button").click();
      await arrival;
      await page.locator("#version").selectOption("0.27.2");
      release();
      await page.waitForFunction(()=>!document.querySelector("#search-button").disabled);
      assert.equal(await page.locator(".evidence-card").count(),0);
      assert.equal(await page.locator("#result-context").isVisible(),false);
      await page.unroute("**/api/search");
    });
    await check("fixture: source markup is displayed only as text",async()=>{
      const unsafe=structuredClone(evidence);
      unsafe.hits[0].text='<img src=x onerror="window.__versionlensXss=true">';
      await page.route("**/api/search",route=>route.fulfill({json:unsafe}));
      await page.locator("#version").selectOption("0.28.1");
      await page.locator("#search-button").click();
      await page.locator(".evidence-card").first().waitFor();
      assert.equal(await page.locator("#result-body img").count(),0);
      assert((await page.locator("#result-body").textContent()).includes("<img src=x"));
      assert.equal(await page.evaluate(()=>window.__versionlensXss),undefined);
      await page.unroute("**/api/search");
    });
    await check("fixture: unsafe source URLs fail closed",async()=>{
      const unsafe=structuredClone(evidence);
      unsafe.hits[0].citation_url="javascript:alert(1)";
      await page.route("**/api/search",route=>route.fulfill({json:unsafe}));
      await page.locator("#search-button").click();
      await page.waitForFunction(()=>document.querySelector("#request-status").classList.contains("is-error"));
      assert.equal(await page.locator(".evidence-card").count(),0);
      assert.equal(await page.locator("#result-body a").count(),0);
      await page.unroute("**/api/search");
    });
    await check("fixture: HTTP failures preserve inputs and show an error",async()=>{
      await page.route("**/api/ask",route=>route.fulfill({status:503,json:{error:{code:"busy",message:"Another query is running. Please try again shortly."}}}));
      await page.locator("#ask-button").click();
      await page.waitForFunction(()=>document.querySelector("#request-status").classList.contains("is-error"));
      assert.equal(await page.locator("#question").inputValue(),evidence.question);
      assert.match(await page.locator("#result-body").textContent(),/Another query is running/);
      await page.unroute("**/api/ask");
    });
    await check("real mobile layout has no horizontal overflow",async()=>{
      await page.setViewportSize({width:360,height:900});
      await page.reload();
      await page.waitForFunction(()=>!document.querySelector("#search-button").disabled);
      await page.locator("#search-button").click();
      await page.locator(".evidence-card").first().waitFor();
      assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));
      await page.locator("h1").click();
      await page.locator(".results").evaluate(el=>el.scrollIntoView({block:"start"}));
      const filename="day4-mobile-evidence.png";
      await page.screenshot({path:path.join(IMAGES,filename),fullPage:false});
      screenshots.push(filename);
    });
    await check("labels, live status and keyboard skip link",async()=>{
      const issues=await page.evaluate(()=>[...document.querySelectorAll("input,select,textarea")].filter(el=>!el.labels?.length).map(el=>el.id));
      assert.deepEqual(issues,[]);
      assert.equal(await page.locator("#request-status").getAttribute("aria-live"),"polite");
      await page.reload();
      await page.waitForFunction(()=>!document.querySelector("#search-button").disabled);
      await page.keyboard.press("Tab");
      assert.equal(await page.evaluate(()=>document.activeElement.classList.contains("skip-link")),true);
      await page.keyboard.press("Enter");
      assert.equal(await page.locator("#question").evaluate(el=>el===document.activeElement),true);
    });
    assert.deepEqual(externalRequests,[]);
    assert.deepEqual(pageErrors,[]);
  } catch(error) {
    failure=error.message;
  } finally {
    const report={kind:"local_browser_integration",recorded_at_utc:new Date().toISOString(),
      browser:browser.version(),origin:origin.origin,status:failure?"failed":"passed",checks,
      generation_checked:process.env.VERSIONLENS_CHECK_GENERATION === "1",
      implementation_sha256:Object.fromEntries([
        ...fs.readdirSync(path.join(ROOT,"src/versionlens")).filter(name=>name.endsWith(".py")).map(name=>`src/versionlens/${name}`),
        "src/versionlens/web/index.html","src/versionlens/web/style.css","src/versionlens/web/app.js","scripts/check_web.cjs"
      ].map(name=>[name,createHash("sha256").update(fs.readFileSync(path.join(ROOT,name))).digest("hex")])),
      screenshots,external_requests:externalRequests,page_errors:pageErrors,
      limitations:["Some negative/race cases use clearly labelled browser fixtures.","Screenshots use actual local API results and no mocked responses.","Labels, focus and responsive checks are not a complete WCAG or screen-reader audit.","This does not measure answer quality or held-out performance."]};
    if(failure)report.error=failure;
    fs.mkdirSync(path.dirname(OUTPUT),{recursive:true});
    fs.writeFileSync(OUTPUT,JSON.stringify(report,null,2)+"\n");
    await browser.close();
  }
  if(failure)throw new Error(failure);
}
main().catch(error=>{console.error(error.message);process.exitCode=1;});
