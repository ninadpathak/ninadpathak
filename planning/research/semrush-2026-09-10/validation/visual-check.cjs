const { chromium } = require('/Users/ninad/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async () => {
 const browser = await chromium.launch({headless:true, executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const results=[];
 for (const [device,width,height] of [['desktop',1440,1000],['mobile',390,844]]) {
  const context=await browser.newContext({viewport:{width,height},deviceScaleFactor:1});
  // Local visual verification should not generate production analytics traffic.
  await context.route(/googletagmanager\.com|google-analytics\.com/,route=>route.abort());
  const page=await context.newPage();
  for (const [name,path] of [['home','/'],['articles','/articles/']]) {
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto('http://127.0.0.1:8769'+path,{waitUntil:'networkidle'});
   await page.screenshot({path:'planning/research/semrush-2026-09-10/validation/'+name+'-'+device+'.png',fullPage:true});
   const state=await page.evaluate(()=>({title:document.title,h1:document.querySelector('h1').innerText,width:innerWidth,scrollWidth:document.documentElement.scrollWidth,articleRows:document.querySelectorAll('.blog-row').length,categoryNav:document.querySelectorAll('[aria-label="Article categories"]').length,tags:document.querySelectorAll('.blog-row .tag').length,links:[...document.querySelectorAll('main a')].map(x=>x.getAttribute('href'))}));
   results.push({name,device,...state,errors});
   if(state.scrollWidth>width||errors.length||name==='articles'&&(state.categoryNav||state.tags)) throw new Error(JSON.stringify(results.at(-1)));
   if(name==='articles') {await page.getByRole('link',{name:'Next →',exact:true}).click(); if(!page.url().endsWith('/articles/page/2/'))throw new Error('Pagination failed');}
  }
  await context.close();
 }
 await browser.close();
 require('fs').writeFileSync('planning/research/semrush-2026-09-10/validation/browser-checks.json',JSON.stringify(results,null,2));
 console.log(JSON.stringify(results.map(({name,device,scrollWidth,width,categoryNav,tags,errors})=>({name,device,scrollWidth,width,categoryNav,tags,errors})),null,2));
})().catch(e=>{console.error(e);process.exit(1)});
