#!/usr/bin/env node
/**
 * merge-pdfs.js — Generate individual chapter PDFs then merge into one book PDF.
 *
 * Usage:
 *   node merge-pdfs.js                  # generate + merge all chapters
 *   node merge-pdfs.js --generate-only  # only generate individual PDFs (no merge)
 *   node merge-pdfs.js --merge-only     # only merge existing PDFs (skip generation)
 *
 * Requires:
 *   - playwright (already in package.json)
 *   - Python 3 + pdfrw  (pip install pdfrw)
 *
 * Output:
 *   docs/statarb-ch*.pdf  — individual chapter PDFs
 *   docs/statarb-BOOK.pdf — merged book
 */

const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

// ── Math book chapter list ──────────────────────────────────────────────────
const MATH_CHAPTERS = [
  'math-index.html',
  'math-part1.html',
  'math-part2.html',
  'math-part3.html',
  'math-part4.html',
  'math-part5.html',
  'math-part6.html',
  'math-part7.html',
  'math-bridge.html',
  'math-appendix-formulas.html',
  'math-appendix-glossary.html',
];

const MATH_BOOK_PDF = path.join(__dirname, 'docs', 'math-BOOK.pdf');

// ── Stat arb chapter list (order = book order) ──────────────────────────────
const CHAPTERS = [
  'statarb-ch0.html',
  'statarb-ch1.html',
  'statarb-ch2.html',
  'statarb-ch3.html',
  'statarb-ch4.html',
  'statarb-ch5.html',
  'statarb-ch6.html',
  'statarb-ch7.html',
  'statarb-ch8.html',
  'statarb-ch9.html',
  'statarb-ch10.html',
  'statarb-ch11.html',
  'statarb-ch12.html',
  'statarb-ch13.html',
  'statarb-ch14.html',
  'statarb-ch15.html',
  'statarb-ch16.html',
  'statarb-ch17.html',
  'statarb-ch18.html',
  'statarb-ch19.html',
  'statarb-ch20.html',
  'statarb-ch21.html',
  'statarb-ch22.html',
  'statarb-ch23.html',
  'statarb-ch24.html',
  'statarb-appendix-formulas.html',
  'statarb-appendix-glossary.html',
];

const DOCS_DIR = path.join(__dirname, 'docs');
const BOOK_PDF = path.join(DOCS_DIR, 'statarb-BOOK.pdf');
const MERGE_SCRIPT = path.join(__dirname, 'tools', 'merge_pdfs.py');

// ── PDF generation ──────────────────────────────────────────────────────────
async function generatePDFs(chapters, bookTitle = 'Statistical Arbitrage') {
  const browser = await chromium.launch();
  const results = [];

  for (const html of chapters) {
    const htmlPath = path.join(DOCS_DIR, html);
    if (!fs.existsSync(htmlPath)) {
      console.warn(`  SKIP (not found): ${html}`);
      continue;
    }

    const pdfPath = htmlPath.replace('.html', '.pdf');
    const slug = path.basename(html, '.html');

    try {
      const page = await browser.newPage();
      await page.goto('file://' + htmlPath, { waitUntil: 'domcontentloaded', timeout: 20000 });
      // Wait for KaTeX and fonts to render
      await page.waitForTimeout(3500);
      await page.pdf({
        path: pdfPath,
        format: 'A4',
        margin: { top: '18mm', bottom: '20mm', left: '18mm', right: '18mm' },
        printBackground: true,
        displayHeaderFooter: true,
        headerTemplate: `<div style="font-size:7.5px;font-family:sans-serif;width:100%;text-align:center;color:#94a3b8;padding-top:4px;">${bookTitle}</div>`,
        footerTemplate: `<div style="font-size:7.5px;font-family:sans-serif;width:100%;text-align:center;color:#94a3b8;padding-bottom:4px;">หน้า <span class="pageNumber"></span> / <span class="totalPages"></span></div>`,
      });
      await page.close();

      const size = fs.statSync(pdfPath).size;
      console.log(`  ✓ ${slug}.pdf — ${(size / 1024).toFixed(0)} KB`);
      results.push(pdfPath);
    } catch (err) {
      console.error(`  ✗ ${slug}: ${err.message}`);
    }
  }

  await browser.close();
  return results;
}

// ── Python merge using pdfrw ────────────────────────────────────────────────
function writeMergeScript() {
  const script = `#!/usr/bin/env python3
"""Merge individual chapter PDFs into one book using pdfrw."""
import sys
import pdfrw

def merge(input_paths, output_path):
    writer = pdfrw.PdfWriter()
    for path in input_paths:
        try:
            reader = pdfrw.PdfReader(path)
            writer.addpages(reader.pages)
            print(f"  + {path} ({len(reader.pages)} pages)")
        except Exception as e:
            print(f"  ! skip {path}: {e}")
    writer.write(output_path)
    import os
    size = os.path.getsize(output_path)
    print(f"\\n  Book PDF: {output_path}")
    print(f"  Size: {size / 1024 / 1024:.1f} MB")

if __name__ == "__main__":
    merge(sys.argv[1:-1], sys.argv[-1])
`;
  fs.writeFileSync(MERGE_SCRIPT, script);
}

function mergePDFs(pdfPaths, outPath = BOOK_PDF) {
  if (pdfPaths.length === 0) {
    console.error('No PDFs to merge.');
    return;
  }
  writeMergeScript();
  const args = [...pdfPaths, outPath].map(p => `"${p}"`).join(' ');
  try {
    execSync(`python3 "${MERGE_SCRIPT}" ${args}`, { stdio: 'inherit' });
  } catch (err) {
    console.error('Merge failed:', err.message);
  }
}

// ── Main ────────────────────────────────────────────────────────────────────
(async () => {
  const args = process.argv.slice(2);
  const generateOnly = args.includes('--generate-only');
  const mergeOnly = args.includes('--merge-only');
  const mathOnly = args.includes('--math');
  const allBooks = args.includes('--all');

  // Select which book to build
  const buildMath = mathOnly || allBooks;
  const buildStatarb = !mathOnly || allBooks;

  async function buildBook(chapters, bookPdf, title) {
    console.log(`\n── ${title} ──────────────────────────────`);
    if (!mergeOnly) {
      console.log(`Generating ${chapters.length} chapter PDFs...`);
      const generated = await generatePDFs(chapters, title);
      console.log(`Generated ${generated.length} PDFs.`);
      if (!generateOnly) {
        console.log('Merging into book PDF...');
        mergePDFs(generated, bookPdf);
      }
    } else {
      console.log('Collecting existing PDFs for merge...');
      const existing = chapters
        .map(html => path.join(DOCS_DIR, html.replace('.html', '.pdf')))
        .filter(p => {
          if (fs.existsSync(p)) return true;
          console.warn(`  SKIP (no PDF): ${path.basename(p)}`);
          return false;
        });
      console.log(`Merging ${existing.length} PDFs...`);
      mergePDFs(existing, bookPdf);
    }
  }

  if (buildStatarb) {
    await buildBook(CHAPTERS, BOOK_PDF, 'Statistical Arbitrage');
  }
  if (buildMath) {
    await buildBook(MATH_CHAPTERS, MATH_BOOK_PDF, 'คณิตศาสตร์สำหรับ Options');
  }

  console.log('\nDone.');
})();
