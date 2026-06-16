#!/usr/bin/env node
/**
 * Pre-render KaTeX math in HTML files to static HTML
 * Usage: node prerender_katex.js input.html output.html
 */
const katex = require('/tmp/node_modules/katex');
const fs    = require('fs');

const [,, inFile, outFile] = process.argv;
let html = fs.readFileSync(inFile, 'utf8');

// Remove KaTeX CDN scripts + auto-render script (math already pre-rendered)
html = html.replace(/<link[^>]*katex[^>]*>/g, '');
html = html.replace(/<script[^>]*katex[^>]*><\/script>/g, '');
// Remove auto-render inline script (prevents script tag corruption artifact)
html = html.replace(/<script>document\.addEventListener[^<]*renderMathInElement[^<]*<\/script>/g, '');

// Add KaTeX CSS inline from local node_modules (for WeasyPrint)
const katexCss = fs.readFileSync('/tmp/node_modules/katex/dist/katex.min.css', 'utf8');
// Replace font URLs with file:// absolute paths (required by WeasyPrint)
const katexFontDir = 'file:///tmp/node_modules/katex/dist/fonts/';
const patchedCss   = katexCss.replace(/url\(fonts\//g, `url(${katexFontDir}`);
html = html.replace('</head>', `<style>${patchedCss}</style>\n</head>`);

// Render display math: $$...$$
html = html.replace(/\$\$([\s\S]*?)\$\$/g, (match, tex) => {
  try {
    return katex.renderToString(tex.trim(), { displayMode: true, throwOnError: false });
  } catch(e) { return match; }
});

// Render inline math: \(...\)
html = html.replace(/\\\(([\s\S]*?)\\\)/g, (match, tex) => {
  try {
    return katex.renderToString(tex.trim(), { displayMode: false, throwOnError: false });
  } catch(e) { return match; }
});

fs.writeFileSync(outFile, html, 'utf8');
console.log(`Done: ${inFile} → ${outFile}`);
