/* Ninad Pathak | Site JS
   Vanilla only. No dependencies. */

(function () {
  'use strict';

  function trackEvent(name, parameters) {
    if (typeof window.gtag !== 'function') return;
    window.gtag('event', name, parameters || {});
  }

  window.trackSiteEvent = trackEvent;

  function getFocusableElements(container) {
    return Array.from(container.querySelectorAll(
      'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), ' +
      'textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )).filter(function (element) {
      return !element.hasAttribute('hidden') && element.getAttribute('aria-hidden') !== 'true';
    });
  }

  function keepFocusInside(event, container) {
    if (event.key !== 'Tab') return;
    const focusable = getFocusableElements(container);
    if (!focusable.length) return;

    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }

  // ----------------------------------------------------------------
  // Theme toggle
  // ----------------------------------------------------------------
  const THEME_KEY = 'np-theme';

  function getStoredTheme() {
    try { return localStorage.getItem(THEME_KEY); } catch { return null; }
  }

  function setTheme(theme) {
    // The critical <style> in base.html keys the page background and color-scheme
    // off data-theme, so the attribute is the only thing to change.
    document.documentElement.setAttribute('data-theme', theme);
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
  // Booking modal
  // ----------------------------------------------------------------
  document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('bookingModal');
    const closeBtn = document.getElementById('bookingModalClose');
    const triggers = document.querySelectorAll('.booking-modal-trigger');
    if (!modal || !triggers.length) return;
    let previousFocus = null;

    function loadBookingWidget() {
      if (document.getElementById('zcalEmbedScript')) return;
      const script = document.createElement('script');
      script.id = 'zcalEmbedScript';
      script.src = 'https://static.zcal.co/embed/v1/embed.js';
      script.async = true;
      document.head.appendChild(script);
    }

    function openModal() {
      previousFocus = document.activeElement;
      modal.removeAttribute('inert');
      modal.classList.add('open');
      modal.setAttribute('aria-hidden', 'false');
      document.body.classList.add('scroll-locked');
      loadBookingWidget();
      if (closeBtn) closeBtn.focus();
    }

    function closeModal() {
      modal.classList.remove('open');
      modal.setAttribute('aria-hidden', 'true');
      modal.setAttribute('inert', '');
      document.body.classList.remove('scroll-locked');
      if (previousFocus) previousFocus.focus();
    }

    triggers.forEach(function (trigger) {
      trigger.addEventListener('click', function (e) {
        e.preventDefault();
        trackEvent('generate_lead', {
          lead_source: 'booking_modal',
          link_text: trigger.textContent.trim(),
          page_path: window.location.pathname
        });
        openModal();
      });
    });

    if (closeBtn) closeBtn.addEventListener('click', closeModal);

    modal.addEventListener('click', function (e) {
      if (e.target === modal || e.target.hasAttribute('data-booking-close')) {
        closeModal();
      }
    });

    document.addEventListener('keydown', function (e) {
      if (!modal.classList.contains('open')) return;
      if (e.key === 'Escape') closeModal();
      else keepFocusInside(e, modal);
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
      mobileNav.removeAttribute('inert');
      mobileNav.classList.add('open');
      mobileNav.setAttribute('aria-hidden', 'false');
      hamburger.setAttribute('aria-expanded', 'true');
      document.body.classList.add('scroll-locked');
      if (closeBtn) closeBtn.focus();
    }

    function closeNav() {
      mobileNav.classList.remove('open');
      mobileNav.setAttribute('aria-hidden', 'true');
      mobileNav.setAttribute('inert', '');
      hamburger.setAttribute('aria-expanded', 'false');
      document.body.classList.remove('scroll-locked');
      hamburger.focus();
    }

    hamburger.addEventListener('click', openNav);
    if (closeBtn) closeBtn.addEventListener('click', closeNav);

    // Close on backdrop click
    mobileNav.addEventListener('click', function (e) {
      if (e.target === mobileNav) closeNav();
    });

    // Close on Escape
    document.addEventListener('keydown', function (e) {
      if (!mobileNav.classList.contains('open')) return;
      if (e.key === 'Escape') closeNav();
      else keepFocusInside(e, mobileNav);
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
    bar.className = 'reading-progress';
    document.body.appendChild(bar);

    let scrollUpdatePending = false;

    function updateScrollProgress() {
      const scrollTop  = window.scrollY;
      const docHeight  = document.documentElement.scrollHeight - window.innerHeight;
      const progress   = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
      // The one inline style left on the site: a per-scroll value no class can hold.
      bar.style.width  = Math.min(100, progress) + '%';
      scrollUpdatePending = false;
    }

    window.addEventListener('scroll', function () {
      if (scrollUpdatePending) return;
      scrollUpdatePending = true;
      window.requestAnimationFrame(updateScrollProgress);
    }, { passive: true });
    updateScrollProgress();
  });

  // ----------------------------------------------------------------
  // Hero canvas — continuous ambient character field (homepage only)
  // ----------------------------------------------------------------
  (function () {
    var canvas = document.getElementById('hero-canvas');
    if (!canvas) return;

    var motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (motionQuery.matches) canvas.hidden = true;

    var ctx      = canvas.getContext('2d');
    var hero     = canvas.closest('.hero');
    var heroCopy = hero ? hero.querySelector('.hero-copy') : null;
    var CHARS    = '0123456789ABCDEF<>{}[]/\\=;()'.split('');
    var CW       = 16;
    var CH       = 22;
    var cells    = [];
    var exclusionRect = null;
    var resizeFrame = null;

    motionQuery.addEventListener('change', function (event) {
      canvas.hidden = event.matches;
      if (event.matches) stopAnimation();
      else {
        resize();
        startAnimation();
      }
    });

    function buildCells() {
      var cols = Math.ceil(canvas.width / CW);
      var rows = Math.ceil(canvas.height / CH);
      cells = [];

      for (var r = 0; r < rows; r++) {
        for (var c = 0; c < cols; c++) {
          cells.push({
            x:            c * CW,
            y:            r * CH,
            char:         CHARS[Math.floor(Math.random() * CHARS.length)],
            alpha:        0,
            state:        'idle',
            timer:        0,
            nextActivate: Math.random() * 2500,
            liveFor:      700 + Math.random() * 1400
          });
        }
      }
    }

    function resize() {
      canvas.width  = hero.offsetWidth;
      canvas.height = hero.offsetHeight;
      buildCells();
      exclusionRect = getExclusionRect();
    }

    function queueResize() {
      if (resizeFrame !== null) return;
      resizeFrame = window.requestAnimationFrame(function () {
        resizeFrame = null;
        resize();
      });
    }

    resize();
    window.addEventListener('resize', queueResize, { passive: true });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(queueResize);

    function getExclusionRect() {
      if (!heroCopy) return null;

      var heroRect = hero.getBoundingClientRect();
      var copyRect = heroCopy.getBoundingClientRect();
      var horizontalPad = window.innerWidth <= 768 ? 28 : 72;
      var verticalPad = window.innerWidth <= 768 ? 24 : 40;

      return {
        left: Math.max(0, copyRect.left - heroRect.left - horizontalPad),
        right: Math.min(canvas.width, copyRect.right - heroRect.left + horizontalPad),
        top: Math.max(0, copyRect.top - heroRect.top - verticalPad),
        bottom: Math.min(canvas.height, copyRect.bottom - heroRect.top + verticalPad)
      };
    }

    function getZoneAlpha(x, y, rect) {
      if (!rect) return 1;

      var feather = window.innerWidth <= 768 ? 18 : 28;
      var insideX = x >= rect.left && x <= rect.right;
      var insideY = y >= rect.top && y <= rect.bottom;

      if (insideX && insideY) return 0;

      var dx = 0;
      if (x < rect.left) dx = rect.left - x;
      else if (x > rect.right) dx = x - rect.right;

      var dy = 0;
      if (y < rect.top) dy = rect.top - y;
      else if (y > rect.bottom) dy = y - rect.bottom;

      var distance = Math.sqrt(dx * dx + dy * dy);
      if (distance >= feather) return 1;
      return Math.max(0, Math.min(1, distance / feather));
    }

    var last = null;
    var animationFrame = null;
    var isIntersecting = true;

    function startAnimation() {
      if (animationFrame !== null || document.hidden || !isIntersecting || motionQuery.matches) return;
      animationFrame = window.requestAnimationFrame(tick);
    }

    function stopAnimation() {
      if (animationFrame !== null) window.cancelAnimationFrame(animationFrame);
      animationFrame = null;
      last = null;
    }

    function tick(ts) {
      animationFrame = null;
      if (document.hidden || !isIntersecting) return;
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
          var zoneAlpha = getZoneAlpha(cell.x + CW / 2, cell.y + CH / 2, exclusionRect);
          if (zoneAlpha <= 0) continue;
          ctx.fillStyle = 'rgba(' + rgb + ',' + (cell.alpha * 0.2 * zoneAlpha) + ')';
          ctx.fillText(cell.char, cell.x + CW / 2, cell.y + CH / 2);
        }
      }

      animationFrame = window.requestAnimationFrame(tick);
    }

    if ('IntersectionObserver' in window) {
      var observer = new IntersectionObserver(function (entries) {
        isIntersecting = entries[0].isIntersecting;
        if (isIntersecting) startAnimation();
        else stopAnimation();
      });
      observer.observe(hero);
    }

    document.addEventListener('visibilitychange', function () {
      if (document.hidden) stopAnimation();
      else startAnimation();
    });

    startAnimation();
  }());

  // ----------------------------------------------------------------
  // Conversion CTA tracking
  // ----------------------------------------------------------------
  document.addEventListener('click', function (event) {
    const link = event.target.closest('a.btn, a.arrow-link');
    if (!link || link.classList.contains('booking-modal-trigger')) return;

    const destination = link.getAttribute('href');
    if (!['/work/', '/portfolio/', '/contact/'].includes(destination)) return;

    trackEvent('cta_click', {
      cta_destination: destination,
      link_text: link.textContent.trim(),
      page_path: window.location.pathname
    });
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

  // ----------------------------------------------------------------
  // Code blocks
  // ----------------------------------------------------------------
  // The build writes each block's frame and language label (code_blocks.py). Script adds
  // only what needs script: a copy button in the head strip, which has a fixed height so
  // nothing shifts, and a focusable, labelled region for code that scrolls sideways,
  // re-checked when the block changes width (rotation, resize).
  const COPY_ICON = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><rect x="5.5" y="5.5" width="8" height="8" rx="1"/><path d="M10.5 3.5v-1a1 1 0 0 0-1-1h-6a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h1"/></svg>';
  const DONE_ICON = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M3 8.5l3 3 7-7"/></svg>';

  function markScrollable(pre, lang) {
    if (pre.scrollWidth > pre.clientWidth + 1) {
      pre.tabIndex = 0;
      pre.setAttribute('role', 'region');
      pre.setAttribute('aria-label', lang + ' code, scrolls sideways');
    } else if (pre.hasAttribute('tabindex')) {
      pre.removeAttribute('tabindex');
      pre.removeAttribute('role');
      pre.removeAttribute('aria-label');
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    const scrollers = [];
    document.querySelectorAll('.code-block').forEach(function (block) {
      const head = block.querySelector('.code-block-head');
      const pre = block.querySelector('pre');
      const code = pre && pre.querySelector('code');
      if (!head || !code) return;
      const lang = block.getAttribute('data-lang') || 'code';

      if (block.classList.contains('code-block--scroll')) {
        scrollers.push([pre, lang]);
        markScrollable(pre, lang);
      }

      if (!navigator.clipboard) return;
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'code-copy';
      button.setAttribute('aria-label', 'Copy ' + lang + ' code');
      button.innerHTML = COPY_ICON + '<span>Copy</span>';
      const status = document.createElement('span');
      status.className = 'code-copy-status';
      status.setAttribute('aria-live', 'polite');
      head.append(button, status);

      let timer = 0;
      function reset() {
        button.classList.remove('is-copied');
        button.innerHTML = COPY_ICON + '<span>Copy</span>';
        status.textContent = '';
      }
      button.addEventListener('click', function () {
        clearTimeout(timer);
        navigator.clipboard.writeText(code.textContent.replace(/\n$/, '')).then(function () {
          button.classList.add('is-copied');
          button.innerHTML = DONE_ICON + '<span>Copied</span>';
          status.textContent = 'Copied to clipboard';
          timer = setTimeout(reset, 2000);
        }).catch(function () {
          status.textContent = 'Copy failed. Select the code and copy it instead.';
          timer = setTimeout(reset, 4000);
        });
      });
    });

    if (scrollers.length && 'ResizeObserver' in window) {
      let frame = 0;
      const observer = new ResizeObserver(function () {
        cancelAnimationFrame(frame);
        frame = requestAnimationFrame(function () {
          scrollers.forEach(function (entry) { markScrollable(entry[0], entry[1]); });
        });
      });
      scrollers.forEach(function (entry) { observer.observe(entry[0]); });
    }
  });

  // ── KEPT VISUAL FALLBACKS ───────────────────────────────────
  // A kept interactive visual keeps its static drawing under the frame. The frame stays
  // transparent until its page says it has drawn, so a blocked or failed frame (a browser
  // error page) shows the drawing. The page posts 'visual-ready' to this window and also
  // sets window.npVisualReady, so the order the two scripts run in doesn't matter: a
  // message that arrives first reveals the frame, and a page that ran before this script
  // is caught by the flag. Neither path waits on the frame's load event, which deferred
  // scripts (Cloudflare Rocket Loader) can fire before the page has drawn.
  function revealFrame(frame) { frame.classList.add('is-ready'); }
  window.addEventListener('message', function (e) {
    if (e.origin !== window.location.origin || !e.data || e.data.type !== 'visual-ready') return;
    document.querySelectorAll('.visual-container--fallback iframe').forEach(function (frame) {
      if (frame.contentWindow === e.source) revealFrame(frame);
    });
  });
  function guardVisuals() {
    const frames = document.querySelectorAll('.visual-container--fallback iframe');
    if (!frames.length) return;
    document.documentElement.classList.add('visuals-guarded');
    frames.forEach(function (frame) {
      try {
        if (frame.contentWindow && frame.contentWindow.npVisualReady) revealFrame(frame);
      } catch (err) { /* error pages are cross-origin: keep the fallback */ }
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', guardVisuals);
  else guardVisuals();

})();
