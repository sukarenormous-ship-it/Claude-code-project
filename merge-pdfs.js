#!/usr/bin/env node
/**
 * merge-pdfs.js — Generate individual chapter PDFs then merge into one book PDF.
 *
 * Usage:
 *   node merge-pdfs.js                  # statarb book (default)
 *   node merge-pdfs.js --math           # math book only
 *   node merge-pdfs.js --vol --pm       # one or more specific books
 *   node merge-pdfs.js --books          # ALL 7 books
 *   node merge-pdfs.js --all            # legacy: math + statarb
 *   node merge-pdfs.js --generate-only  # only generate individual PDFs (no merge)
 *   node merge-pdfs.js --merge-only     # only merge existing PDFs (skip generation)
 *
 * Book keys: math, vp, pm, vol, arb, eye, statarb
 *
 * Requires:
 *   - playwright (already in package.json)
 *   - Python 3 + pdfrw  (pip install pdfrw)
 *
 * Output:
 *   docs/<book>-*.pdf     — individual chapter PDFs
 *   docs/<book>-BOOK.pdf  — merged book (e.g. statarb-BOOK.pdf, vol-BOOK.pdf)
 */

const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

const DOCS_DIR = path.join(__dirname, 'docs');
const MERGE_SCRIPT = path.join(__dirname, 'tools', 'merge_pdfs.py');

// ── Book registry ───────────────────────────────────────────────────────────
// Each book: key (CLI flag), title (PDF header), output filename, chapters in
// reading order. `node merge-pdfs.js --<key>` builds one book; --books = all.
const BOOKS = {
  math: {
    title: 'คณิตศาสตร์สำหรับ Options',
    output: 'math-BOOK.pdf',
    chapters: [
      'math-index.html',
      'math-part1.html', 'math-part2.html', 'math-part3.html', 'math-part4.html',
      'math-part5.html', 'math-part6.html', 'math-part7.html',
      'math-bridge.html',
      'math-appendix-formulas.html', 'math-appendix-glossary.html',
    ],
  },
  vp: {
    title: 'View → Payoff',
    output: 'vp-BOOK.pdf',
    chapters: [
      'vp-part1.html', 'vp-part2.html', 'vp-part3.html', 'vp-part4.html',
      'vp-part5.html', 'vp-part6.html', 'vp-part7.html', 'vp-drills.html',
    ],
  },
  pm: {
    title: 'Payoff Mastery',
    output: 'pm-BOOK.pdf',
    chapters: [
      'pm-part0.html', 'pm-part1.html', 'pm-part2.html', 'pm-part3.html',
      'pm-part3a.html', 'pm-part4.html', 'pm-part4a.html', 'pm-part5.html',
      'pm-part5a.html', 'pm-part6.html', 'pm-part7.html', 'pm-part8.html',
    ],
  },
  vol: {
    title: 'Volatility Mastery',
    output: 'vol-BOOK.pdf',
    chapters: [
      'vol-part1.html', 'vol-part2.html', 'vol-part3.html', 'vol-part4.html',
      'vol-part5.html', 'vol-part6.html', 'vol-part7.html', 'vol-part8.html',
    ],
  },
  arb: {
    title: 'Arbitrage — จากแนวคิดสู่การปฏิบัติ',
    output: 'arb-BOOK.pdf',
    chapters: [
      'arb-part1.html', 'arb-part2a.html', 'arb-part2b.html', 'arb-part3.html',
      'arb-part4.html', 'arb-part5.html', 'arb-part6.html', 'arb-part7.html',
      'arb-part8.html', 'arb-part9.html',
    ],
  },
  eye: {
    title: 'ตาของ Arbitrageur',
    output: 'eye-BOOK.pdf',
    chapters: [
      'eye-part1.html', 'eye-part2.html', 'eye-part3.html', 'eye-part4.html',
      'eye-part5.html',
    ],
  },
  statarb: {
    title: 'Statistical Arbitrage',
    output: 'statarb-BOOK.pdf',
    chapters: [
      'statarb-ch0.html', 'statarb-ch1.html', 'statarb-ch2.html', 'statarb-ch3.html',
      'statarb-ch4.html', 'statarb-ch5.html', 'statarb-ch6.html', 'statarb-ch7.html',
      'statarb-ch8.html', 'statarb-ch9.html', 'statarb-ch10.html', 'statarb-ch11.html',
      'statarb-ch12.html', 'statarb-ch13.html', 'statarb-ch14.html', 'statarb-ch15.html',
      'statarb-ch16.html', 'statarb-ch17.html', 'statarb-ch18.html', 'statarb-ch19.html',
      'statarb-ch20.html', 'statarb-ch21.html', 'statarb-ch22.html', 'statarb-ch23.html',
      'statarb-ch24.html',
      'statarb-appendix-formulas.html', 'statarb-appendix-glossary.html',
    ],
  },
};

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

function mergePDFs(pdfPaths, outPath) {
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
  const allBooks = args.includes('--books') || args.includes('--all-books');

  // Backward-compat: --all = math + statarb (legacy). --math = math only.
  const legacyAll = args.includes('--all');
  const mathOnly = args.includes('--math');

  // Determine which book keys to build.
  let keys;
  if (allBooks) {
    keys = Object.keys(BOOKS);                        // all 7
  } else if (legacyAll) {
    keys = ['statarb', 'math'];                       // legacy --all
  } else if (mathOnly) {
    keys = ['math'];
  } else {
    // Any explicit per-book flags (--vol, --pm, --arb, ...)?
    const explicit = Object.keys(BOOKS).filter(k => args.includes(`--${k}`));
    keys = explicit.length ? explicit : ['statarb'];  // default = statarb
  }

  async function buildBook(book) {
    const bookPdf = path.join(DOCS_DIR, book.output);
    console.log(`\n── ${book.title} ──────────────────────────────`);
    if (!mergeOnly) {
      console.log(`Generating ${book.chapters.length} chapter PDFs...`);
      const generated = await generatePDFs(book.chapters, book.title);
      console.log(`Generated ${generated.length} PDFs.`);
      if (!generateOnly) {
        console.log('Merging into book PDF...');
        mergePDFs(generated, bookPdf);
      }
    } else {
      console.log('Collecting existing PDFs for merge...');
      const existing = book.chapters
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

  for (const key of keys) {
    await buildBook(BOOKS[key]);
  }

  console.log('\nDone.');
})();
