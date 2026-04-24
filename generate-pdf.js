const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path');

const files = process.argv.slice(2);
if (files.length === 0) {
  console.log('Usage: node generate-pdf.js <html-file> [html-file ...]');
  process.exit(1);
}

(async () => {
  const browser = await chromium.launch();
  for (const htmlFile of files) {
    const page = await browser.newPage();
    const filePath = path.resolve(__dirname, htmlFile);
    const pdfPath = filePath.replace('.html', '.pdf');
    const title = path.basename(htmlFile, '.html');
    await page.goto('file://' + filePath, { waitUntil: 'domcontentloaded', timeout: 15000 });
    await page.waitForTimeout(3000);
    await page.pdf({
      path: pdfPath,
      format: 'A4',
      margin: { top: '20mm', bottom: '20mm', left: '18mm', right: '18mm' },
      printBackground: true,
      displayHeaderFooter: true,
      headerTemplate: `<div style="font-size:8px;font-family:Sarabun,sans-serif;width:100%;text-align:center;color:#94a3b8;">Payoff Mastery — ${title}</div>`,
      footerTemplate: '<div style="font-size:8px;font-family:Sarabun,sans-serif;width:100%;text-align:center;color:#94a3b8;">หน้า <span class="pageNumber"></span> / <span class="totalPages"></span></div>'
    });
    await page.close();
    const fs = require('fs');
    const stats = fs.statSync(pdfPath);
    console.log(`${pdfPath} — ${(stats.size / 1024).toFixed(0)} KB`);
  }
  await browser.close();
  console.log('All PDFs generated!');
})();
