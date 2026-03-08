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
    try { localStorage.setItem(THEME_KEY, theme); } catch {}
  }

  // Apply saved theme immediately (avoids flash)
  const savedTheme = getStoredTheme();
  if (savedTheme) setTheme(savedTheme);

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

})();
