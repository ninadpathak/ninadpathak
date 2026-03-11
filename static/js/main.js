/* Ninad Pathak | Site JS
   Vanilla only. No dependencies. */

(function () {
  'use strict';

  // ----------------------------------------------------------------
  // Theme toggle
  // ----------------------------------------------------------------
  const THEME_KEY = 'np-theme';

  function getStoredTheme() {
    try { return localStorage.getItem(THEME_KEY); } catch { return null; }
  }

  function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.style.colorScheme = theme === 'light' ? 'light' : 'dark';
    document.documentElement.style.backgroundColor = theme === 'light' ? '#f8f8f6' : '#090909';
    try { localStorage.setItem(THEME_KEY, theme); } catch {}
  }

  // Apply saved theme immediately (avoids flash)
  const savedTheme = getStoredTheme();
  if (savedTheme) setTheme(savedTheme);

  function releaseThemePreload() {
    window.requestAnimationFrame(function () {
      document.documentElement.classList.remove('theme-preload');
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', releaseThemePreload, { once: true });
  } else {
    releaseThemePreload();
  }

  document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('themeToggle');
    if (!btn) return;
    btn.addEventListener('click', function () {
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      setTheme(current === 'dark' ? 'light' : 'dark');
    });
  });

  // ----------------------------------------------------------------
  // Mobile nav
  // ----------------------------------------------------------------
  document.addEventListener('DOMContentLoaded', function () {
    const hamburger  = document.getElementById('hamburger');
    const mobileNav  = document.getElementById('mobileNav');
    const closeBtn   = document.getElementById('mobileClose');

    if (!hamburger || !mobileNav) return;

    function openNav() {
      mobileNav.classList.add('open');
      mobileNav.setAttribute('aria-hidden', 'false');
      hamburger.setAttribute('aria-expanded', 'true');
      document.body.style.overflow = 'hidden';
    }

    function closeNav() {
      mobileNav.classList.remove('open');
      mobileNav.setAttribute('aria-hidden', 'true');
      hamburger.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    }

    hamburger.addEventListener('click', openNav);
    if (closeBtn) closeBtn.addEventListener('click', closeNav);

    // Close on backdrop click
    mobileNav.addEventListener('click', function (e) {
      if (e.target === mobileNav) closeNav();
    });

    // Close on Escape
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && mobileNav.classList.contains('open')) closeNav();
    });
  });

  // ----------------------------------------------------------------
  // Portfolio filter
  // ----------------------------------------------------------------
  document.addEventListener('DOMContentLoaded', function () {
    const filterGroup = document.getElementById('portfolioFilters');
    const grid        = document.getElementById('portfolioGrid');
    if (!filterGroup || !grid) return;

    const items = Array.from(grid.querySelectorAll('.p-item'));

    filterGroup.addEventListener('click', function (e) {
      const btn = e.target.closest('.filter-btn');
      if (!btn) return;

      // Update active state
      filterGroup.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const filter = btn.getAttribute('data-filter');

      items.forEach(function (item) {
        if (filter === 'all' || item.getAttribute('data-cat') === filter) {
          item.hidden = false;
        } else {
          item.hidden = true;
        }
      });
    });
  });

  // ----------------------------------------------------------------
  // Scroll progress bar on blog posts
  // ----------------------------------------------------------------
  document.addEventListener('DOMContentLoaded', function () {
    const postBody = document.querySelector('.post-body');
    if (!postBody) return;

    // Create bar
    const bar = document.createElement('div');
    bar.style.cssText = [
      'position: fixed',
      'top: 0',
      'left: 0',
      'height: 2px',
      'width: 0%',
      'background: var(--accent)',
      'z-index: 999',
      'transition: width 0.1s linear',
      'pointer-events: none',
    ].join(';');
    document.body.appendChild(bar);

    window.addEventListener('scroll', function () {
      const scrollTop  = window.scrollY;
      const docHeight  = document.documentElement.scrollHeight - window.innerHeight;
      const progress   = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
      bar.style.width  = Math.min(100, progress) + '%';
    }, { passive: true });
  });

  // ----------------------------------------------------------------
  // Hero canvas — continuous ambient character field (homepage only)
  // ----------------------------------------------------------------
  (function () {
    var canvas = document.getElementById('hero-canvas');
    if (!canvas) return;

    var ctx   = canvas.getContext('2d');
    var hero  = canvas.closest('.hero');
    var CHARS = '0123456789ABCDEF<>{}[]/\\=;()'.split('');
    var CW    = 16;
    var CH    = 22;

    function resize() {
      canvas.width  = hero.offsetWidth;
      canvas.height = hero.offsetHeight;
    }
    resize();
    window.addEventListener('resize', resize, { passive: true });

    var cols  = Math.ceil(canvas.width  / CW);
    var rows  = Math.ceil(canvas.height / CH);

    // Each cell cycles: idle → fade-in → live (scrambling) → fade-out → idle
    var cells = [];
    for (var r = 0; r < rows; r++) {
      for (var c = 0; c < cols; c++) {
        cells.push({
          x:            c * CW,
          y:            r * CH,
          char:         CHARS[Math.floor(Math.random() * CHARS.length)],
          alpha:        0,
          state:        'idle',
          timer:        0,
          // Stagger the initial activations so they don't all fire at once
          nextActivate: Math.random() * 2500,
          liveFor:      700 + Math.random() * 1400
        });
      }
    }

    var last = null;

    function tick(ts) {
      if (!last) last = ts;
      var dt  = Math.min(ts - last, 64); // cap at ~2 frames to avoid jumps after tab switch
      last    = ts;

      var isDark = document.documentElement.getAttribute('data-theme') !== 'light';
      var rgb    = isDark ? '255,95,31' : '140,45,0';

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.font         = (CH - 6) + "px 'JetBrains Mono', monospace";
      ctx.textAlign    = 'center';
      ctx.textBaseline = 'middle';

      for (var i = 0; i < cells.length; i++) {
        var cell = cells[i];
        cell.timer += dt;

        if (cell.state === 'idle') {
          if (cell.timer >= cell.nextActivate) {
            cell.state = 'in';
            cell.timer = 0;
            cell.char  = CHARS[Math.floor(Math.random() * CHARS.length)];
          }
          continue;
        }

        if (cell.state === 'in') {
          cell.alpha = Math.min(cell.timer / 220, 1);
          if (cell.alpha >= 1) { cell.state = 'live'; cell.timer = 0; }

        } else if (cell.state === 'live') {
          // Occasionally flip the character
          if (Math.random() < 0.008) {
            cell.char = CHARS[Math.floor(Math.random() * CHARS.length)];
          }
          if (cell.timer >= cell.liveFor) { cell.state = 'out'; cell.timer = 0; }

        } else if (cell.state === 'out') {
          cell.alpha = Math.max(1 - cell.timer / 280, 0);
          if (cell.alpha <= 0) {
            cell.state        = 'idle';
            cell.timer        = 0;
            cell.nextActivate = 800 + Math.random() * 3500;
            cell.liveFor      = 700 + Math.random() * 1400;
          }
        }

        if (cell.alpha > 0) {
          ctx.fillStyle = 'rgba(' + rgb + ',' + (cell.alpha * 0.2) + ')';
          ctx.fillText(cell.char, cell.x + CW / 2, cell.y + CH / 2);
        }
      }

      requestAnimationFrame(tick);
    }

    requestAnimationFrame(tick);
  }());

  // ----------------------------------------------------------------
  // Active nav link
  // ----------------------------------------------------------------
  document.addEventListener('DOMContentLoaded', function () {
    const path  = window.location.pathname;
    const links = document.querySelectorAll('.nav-link');
    links.forEach(function (link) {
      const href = link.getAttribute('href');
      if (href && href !== '/' && path.startsWith(href)) {
        link.classList.add('active');
      }
    });
  });

  // ----------------------------------------------------------------
  // Copy code buttons for code blocks
  // ----------------------------------------------------------------
  document.addEventListener('DOMContentLoaded', function () {
    const codeBlocks = document.querySelectorAll('.highlight pre');
    
    codeBlocks.forEach(function (pre) {
      // Create wrapper if not already wrapped
      let wrapper = pre.parentElement;
      if (!wrapper.classList.contains('code-block-wrapper')) {
        wrapper = document.createElement('div');
        wrapper.className = 'code-block-wrapper';
        pre.parentNode.insertBefore(wrapper, pre);
        wrapper.appendChild(pre);
      }
      
      // Create copy button
      const button = document.createElement('button');
      button.className = 'copy-code-btn';
      button.setAttribute('aria-label', 'Copy code to clipboard');
      button.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';
      
      // Add click handler
      button.addEventListener('click', function () {
        const code = pre.textContent;
        navigator.clipboard.writeText(code).then(function () {
          button.classList.add('copied');
          button.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>';
          
          setTimeout(function () {
            button.classList.remove('copied');
            button.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';
          }, 2000);
        }).catch(function () {
          button.style.color = 'var(--accent)';
          setTimeout(function () {
            button.style.color = '';
          }, 2000);
        });
      });
      
      wrapper.appendChild(button);
    });
  });

})();
