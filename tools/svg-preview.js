const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const page = await browser.newPage({ deviceScaleFactor: 2 });
  const files = ['ch3-halflife-zones','ch3-ar1-bvalues','ch3-walkforward'];
  for (const f of files) {
    await page.goto('file:///home/user/Claude-code-project/docs/charts/'+f+'.svg', {waitUntil:'networkidle'});
    const el = await page.$('svg');
    await el.screenshot({ path: '/tmp/'+f+'.png' });
  }
  await browser.close();
  console.log('previews rendered');
})();
