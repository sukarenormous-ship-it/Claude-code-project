const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const ch = process.argv[2] || 'statarb-ch3';
(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const page = await browser.newPage();
  await page.goto('file:///home/user/Claude-code-project/docs/'+ch+'.html', { waitUntil:'networkidle', timeout:45000 });
  // ensure KaTeX finished
  await page.waitForFunction(() => !document.querySelector('.ki-eq')?.textContent.includes('$$') , {timeout:8000}).catch(()=>{});
  await page.waitForTimeout(1500);
  await page.pdf({ path:'/home/user/Claude-code-project/docs/'+ch+'.pdf', format:'A4',
    margin:{top:'18mm',bottom:'18mm',left:'16mm',right:'16mm'}, printBackground:true });
  // full-page screenshot of just the math+chart region for review
  await page.setViewportSize({width:920, height:1400});
  await page.screenshot({ path:'/tmp/'+ch+'-full.png', fullPage:true });
  await browser.close();
  console.log('rendered', ch, '-> pdf + full png');
})();
