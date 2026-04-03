const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  const filePath = path.resolve(__dirname, 'docs/payoff-chart-study-guide.html');
  await page.goto('file://' + filePath, { waitUntil: 'domcontentloaded', timeout: 15000 });

  // Wait for rendering
  await page.waitForTimeout(3000);

  await page.pdf({
    path: path.resolve(__dirname, 'docs/payoff-chart-study-guide.pdf'),
    format: 'A4',
    margin: { top: '20mm', bottom: '20mm', left: '18mm', right: '18mm' },
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: '<div style="font-size:8px;font-family:Sarabun,sans-serif;width:100%;text-align:center;color:#94a3b8;">Payoff Chart Study Guide</div>',
    footerTemplate: '<div style="font-size:8px;font-family:Sarabun,sans-serif;width:100%;text-align:center;color:#94a3b8;">หน้า <span class="pageNumber"></span> / <span class="totalPages"></span></div>'
  });

  await browser.close();
  console.log('PDF created successfully!');
})();
