# Add Diagram

Add a MiniChart (line, bar, or bell) to an HTML part in any book.

**Usage:** `/add-diagram <prefix-partname> <chart-type> <description>`

Examples:
- `/add-diagram vol-part3 bar "VOL regime comparison — IV, RV, IVR"`
- `/add-diagram statarb-ch5 line "Spread mean-reversion over 20 weeks"`
- `/add-diagram pm-part2 bell "Kelly position size distribution"`

## Steps

The argument is: $ARGUMENTS

Parse: 
- Word 1 = full part filename without `.html` (e.g. `vol-part3`)
- Word 2 = chart type: `line`, `bar`, or `bell`
- Remaining words = description of what the chart should show

### File path
`/home/user/Claude-code-project/docs/{word1}.html`

### MiniChart API (from docs/vendor/chartjs/mini-charts.js)

**Line chart:**
```javascript
MiniChart.line(element, {
  title: 'Chart Title',
  labels: ['L1','L2',...],          // x-axis labels
  datasets: [
    { label: 'Series', color: '#06b6d4', fill: true/false, data: [v1,v2,...] }
  ],
  yMin: -100, yMax: 100, yLabel: 'Y axis label',
  caption: 'Thai caption text'       // optional
});
```

**Bar chart (grouped):**
```javascript
MiniChart.bar(element, {
  title: 'Chart Title',
  groups: ['G1','G2','G3'],          // x-axis group labels (use \n for line break)
  datasets: [
    { label: 'Series', color: '#06b6d4', data: [v1,v2,v3] }
  ],
  yLabel: 'Y label'
});
```

**Bell curve:**
```javascript
MiniChart.bell(element, {
  title: 'Chart Title',
  mean: 0, sd: 1,
  xMin: -3, xMax: 3,
  fillColor: '#06b6d4',
  caption: 'caption text'
});
```

### Color palette (use in order)
- Primary: `#06b6d4` (cyan)
- Secondary: `#7c3aed` (violet)
- Positive/up: `#16a34a` (green)
- Negative/down: `#dc2626` (red)
- Neutral: `#f59e0b` (amber)
- Muted: `#64748b` (slate)

### Insertion rule
- Read the target HTML file
- Find the most relevant heading (h2 or h3) near the described topic
- Insert AFTER the next `</p>` or `</ul>` following that heading
- Use this wrapper template:

```html
<canvas id="chart{UniqueId}" class="chart" style="height:280px"></canvas>
<p class="caption">{Thai caption describing what the chart shows}</p>
<script>
(function(){
  MiniChart.{type}(document.getElementById('chart{UniqueId}'), {
    // ... parameters ...
  });
})();
</script>
```

### Steps
1. Read the HTML file to understand the content around the target section
2. Choose realistic data values that match the book's actual numbers (read surrounding text for reference values)
3. Write the chart block
4. Insert it into the file using Edit
5. Screenshot the part at 703px width to verify the chart renders
6. Report what was added and where
