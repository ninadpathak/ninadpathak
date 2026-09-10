const {spawn}=require('child_process');
const fs=require('fs');
const {chromium}=require('/Users/ninad/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const evidence='planning/research/writing-refresh-2026-09-10/';
(async()=>{const server=spawn('python3',['-u','-m','http.server','0','--bind','127.0.0.1','--directory','output'],{stdio:['ignore','pipe','ignore']});let browser;try{
const port=await new Promise((resolve,reject)=>{server.stdout.on('data',x=>{const m=x.toString().match(/port (\d+)/);if(m)resolve(m[1]);});server.on('error',reject);});
browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
const pages=[['tutorial','how-to-write-a-technical-tutorial-that-actually-teaches',3,5],['template','technical-documentation-template',4,4],['examples','technical-writing-examples',7,6]];
const results=[];
for(const [device,width,height] of [['desktop',1440,1000],['mobile',390,844]]){const context=await browser.newContext({viewport:{width,height}});await context.route(/googletagmanager\.com|google-analytics\.com/,r=>r.abort());const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
for(const [name,slug,tableCount,lastRows] of pages){const response=await page.goto(`http://127.0.0.1:${port}/articles/${slug}/`,{waitUntil:'networkidle'});const state=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,tables:[...document.querySelectorAll('.post-content table')].map(t=>({headings:[...t.querySelectorAll('th')].map(x=>x.innerText),rows:t.querySelectorAll('tbody tr').length})),strayPipes:[...document.querySelectorAll('.post-content p')].filter(p=>/^\s*\|/.test(p.innerText)).length}));
await page.screenshot({path:evidence+name+'-'+device+'.png',fullPage:true});
await page.locator('.post-content table').last().screenshot({path:evidence+name+'-final-table-'+device+'.png'});
const result={name,device,status:response.status(),...state,errors:[...errors]};results.push(result);
if(response.status()!==200||state.scrollWidth>width||state.strayPipes||errors.length||state.tables.length!==tableCount||state.tables.at(-1).rows!==lastRows)throw Error(JSON.stringify(result));}
await context.close();}
fs.writeFileSync(evidence+'render-checks.json',JSON.stringify(results,null,2));console.log(JSON.stringify(results,null,2));
}finally{if(browser)await browser.close();server.kill('SIGTERM');}})().catch(e=>{console.error(e);process.exit(1)});
