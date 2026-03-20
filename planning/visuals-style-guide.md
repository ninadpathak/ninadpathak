# Technical Visuals Style Guide

This document defines the constraints, architecture, and design language for all interactive and animated visuals across the blog. 

The core philosophy is **Technical Precision**. Visuals must feel like native UI components of the site—clean, exact, and strictly utilitarian. No decorative gradients, no bouncy physics, and no unnecessary drop shadows.

---

## 1. Container Architecture

Visuals are embedded into Markdown posts using a strict HTML container structure. This ensures the visual's title sits *inside* the main bounding box, perfectly aligned with the site's layout.

```html
<div class="visual-wrapper">
  <!-- Title always uses the '//' prefix via CSS -->
  <div class="visual-title">Title of the Visual Goes Here</div>
  <div class="visual-container">
    <iframe src="/static/visuals/your-visual-file.html" title="Accessibility Title" loading="lazy"></iframe>
  </div>
</div>
```

**Key rules for the wrapper:**
- Do not use `<span>Animated Visual</span>` in the title. Let the visual speak for itself.
- The `visuals.css` file handles the borders and spacing. The `iframe` should take up 100% of the container.

---

## 2. Standalone Visual Files

The actual visuals are self-contained HTML files stored in `static/visuals/`. They must contain their own CSS and JS. 

### Design Tokens
Every visual must replicate the site's core CSS custom properties to ensure perfect Light/Dark mode syncing. Paste this exact `:root` block into the `<style>` of every new visual:

```css
:root {
    --bg-1: #ffffff;
    --bg-2: #efefed;
    --border: #e0e0dc;
    --text-1: #0e0e0e;
    --text-2: #3a3a3a;
    --text-3: #888888;
    --accent: #d44000;
    --mono: 'JetBrains Mono', 'SF Mono', 'Fira Code', 'Courier New', monospace;
    --sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

@media (prefers-color-scheme: dark) {
    :root {
        --bg-1: #111111;
        --bg-2: #1a1a1a;
        --border: #1e1e1e;
        --text-1: #f0f0f0;
        --text-2: #c2c2c2;
        --text-3: #6a6a6a;
        --accent: #ff5f1f;
    }
}

body { 
    margin: 0; 
    background: var(--bg-1); 
    font-family: var(--sans); 
    color: var(--text-1);
    overflow: hidden; 
}
```

### Design Constraints
- **Borders:** Use solid 1px borders (`1px solid var(--border)`).
- **Backgrounds:** Stick to `var(--bg-1)` for bases and `var(--bg-2)` for subtle highlights or active states.
- **Accents:** Use `var(--accent)` for the most critical moving parts or active data (e.g., the final vector numbers, the active scanning line).
- **Typography:** Use the monospace font (`var(--mono)`) for code, data arrays, labels, and metrics. Use the sans-serif font (`var(--sans)`) for explanatory text.
- **Animations:** Animations should feel mechanical and linear. Avoid exaggerated `bounce` or `elastic` easing. Use `ease` or linear movements. Things should snap, slide, or fade deliberately.

---

## 3. 3D Requirements (Three.js)

When building 3D visuals using Three.js:
1. Use `THREE.WebGLRenderer({ antialias: true, alpha: true })`.
2. The scene background should read the CSS variable or color scheme: 
   `scene.background = new THREE.Color(isDark ? 0x111111 : 0xffffff);`
3. Always include a native resize listener so the canvas scales smoothly within the iframe container:
   ```javascript
   window.addEventListener('resize', () => {
       camera.aspect = window.innerWidth / window.innerHeight;
       camera.updateProjectionMatrix();
       renderer.setSize(window.innerWidth, window.innerHeight);
   });
   ```
4. 3D elements should rely on clean lines (`LineBasicMaterial`), points (`PointsMaterial`), and simple geometry. Avoid complex lighting or shaders unless technically necessary to explain the concept.

---

## 4. Mobile Responsiveness

Visuals must not break on mobile devices. Because they are loaded via iframes, the responsive logic must exist *inside* the standalone visual HTML file.

- **Stacking:** If a visual relies on horizontal flow (e.g., `Stage 1 -> Stage 2` or horizontal chunking), use a media query at `max-width: 600px` to flip the flex-direction to `column`.
- **Padding:** Always use `box-sizing: border-box` and ensure containers have inner padding (e.g., `padding: 2rem`) so elements don't touch the very edges of the iframe.
- **Iframe Height:** The main site's `visuals.css` bumps the iframe height to `500px` on mobile screens to accommodate elements that stack vertically. Ensure your vertical layouts fit within this constraint.
