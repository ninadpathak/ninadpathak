/* Process page (/technical-writing-process/). Needs GSAP, ScrollTrigger and SplitText,
   which the page loads before this file.

   The page is complete without any of it. A line in the page head adds .pp-js when
   motion is welcome, and process.css then pins each built scene's stage to the window.
   This file scrubs those scenes with the scroll: the headline arrives, shrinks into the
   bar of the object it names, and the object's own text plays one caption at a time.
   When it has set the scenes up it marks <html> with data-pp-ready; if that never
   happens the head script takes .pp-js off and the page stays plain.

   Cloudflare Rocket Loader runs this after load, so a reader may already be mid-page.
   Every timeline is tied to scroll position, so it starts wherever the page is. */
(function () {
  'use strict';

  var root = document.documentElement;
  var each = function (list, fn) { Array.prototype.forEach.call(list, fn); };

  // The rail marks the stage on screen, staged or plain.
  var links = {};
  each(document.querySelectorAll('.pp-rail-link'), function (link) { links[link.getAttribute('href').slice(1)] = link; });
  var rail = document.querySelector('.pp-rail');
  var page = document.querySelector('.pp');
  if (!page || !('IntersectionObserver' in window)) return;
  var current = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      var link = links[entry.target.id];
      if (!link) return;
      if (entry.isIntersecting) link.setAttribute('aria-current', 'step');
      else link.removeAttribute('aria-current');
    });
    rail.classList.toggle('is-on', !!rail.querySelector('[aria-current]'));
  }, { rootMargin: '-45% 0px -55% 0px' });
  each(page.querySelectorAll('.pp-scene'), function (scene) { current.observe(scene); });
  var gsap = window.gsap, ScrollTrigger = window.ScrollTrigger, SplitText = window.SplitText;
  if (!root.classList.contains('pp-js') || !gsap || !ScrollTrigger || !SplitText) return;
  gsap.registerPlugin(ScrollTrigger, SplitText);

  // Split text starts hidden and is revealed with to(): a from() tween on a timeline that
  // is invalidated on refresh re-reads its start value and can leave a letter behind.
  var chars = function (el, from) {
    var parts = new SplitText(el, { type: 'words,chars' }).chars;
    gsap.set(parts, from || { opacity: 0 });
    return parts;
  };
  var words = function (el) { return new SplitText(el, { type: 'words' }).words; };

  // Where an element sits on its stage, ignoring any transform.
  function place(el, stage) {
    var x = 0, y = 0;
    for (var node = el; node && node !== stage; node = node.offsetParent) { x += node.offsetLeft; y += node.offsetTop; }
    return { x: x, y: y };
  }

  // The headline shrinks into the object's bar. The bar is centred on the stage's axis and
  // so is the headline, so only the scale decides the sideways move. The dock is an empty
  // line in the bar, given the shrunken headline's height so the bar keeps room for it.
  function docking(scene) {
    var stage = scene.querySelector('.pp-stage'), head = scene.querySelector('.pp-head');
    var bar = scene.querySelector('.pp-bar'), dock = scene.querySelector('.pp-dock');
    var to = { x: 0, y: 0, scale: 1 };
    function measure() {
      var style = window.getComputedStyle(head);
      var width = parseFloat(style.width), height = parseFloat(style.height);
      to.scale = parseFloat(window.getComputedStyle(bar).fontSize) * 1.15 / parseFloat(style.fontSize);
      gsap.set(dock, { height: height * to.scale });
      // Offsets give the headline's anchor; it is drawn half its size up and left of it.
      to.x = (width - width * to.scale) / 2;
      to.y = place(dock, stage).y - (place(head, stage).y - height / 2);
    }
    // The column is a 3D space, where the object would otherwise paint over the headline.
    // The headline is centred on its anchor here, since GSAP owns its transform (it
    // clears a CSS `translate` on anything it animates).
    gsap.set(head, { z: 1, xPercent: -50, yPercent: -50, transformOrigin: '0 0' });
    measure();
    ScrollTrigger.addEventListener('refreshInit', measure);
    return { x: function () { return to.x; }, y: function () { return to.y; }, scale: function () { return to.scale; } };
  }

  // One caption at a time: each arrives from below and leaves upward.
  function captions(timeline, scene, times) {
    var caps = scene.querySelectorAll('.pp-cap');
    gsap.set(caps, { autoAlpha: 0, y: 14 });
    each(caps, function (cap, index) {
      timeline.to(cap, { autoAlpha: 1, y: 0, duration: 0.5 }, times[index]);
      timeline.to(cap, { autoAlpha: 0, y: -14, duration: 0.4, ease: 'power2.in' }, times[index + 1] - 0.45);
    });
  }

  function scrubbed(scene) {
    return gsap.timeline({
      defaults: { ease: 'power2.out' },
      scrollTrigger: { trigger: scene, start: 'top top', end: 'bottom bottom', scrub: 0.5, invalidateOnRefresh: true },
    });
  }

  var rise = function () { return window.innerHeight * 0.36; };
  var lying = { rotationX: 62, y: rise, scale: 0.82, transformOrigin: '50% 50%' };
  // On a narrow window the title fills the stage, so the thread waits out of sight.
  var resting = function () { return window.innerWidth < 700 ? 0 : 0.4; };
  var gone = { rotationX: -55, yPercent: -55, scale: 0.8, opacity: 0, duration: 1.2, ease: 'power2.in' };

  // ---- The opening and the issue ------------------------------------------------
  (function () {
    var scene = document.getElementById('issue');
    if (!scene) return;
    var q = function (selector) { return scene.querySelectorAll(selector); };
    var obj = q('.pp-obj')[0], head = q('.pp-head')[0], dock = docking(scene);
    var tl = scrubbed(scene);

    gsap.set(q('.pp-col'), { visibility: 'visible' });
    gsap.set(obj, Object.assign({ opacity: resting }, lying));
    gsap.set([q('.pp-kick'), q('.pi-labels > *'), q('.pi-source')], { opacity: 0 });
    gsap.set(q('.pi-linked'), { opacity: 0, y: 12 });
    gsap.set(q('.pi-comment'), { opacity: 0, x: -18 });
    gsap.set(q('.pi-dup'), { opacity: 0, scale: 0.6 });
    gsap.set(q('.pi-demand i'), { scaleY: 0 });
    gsap.set(q('.pi-demand svg'), { opacity: 0 });

    // The title gives way.
    tl.to(words(q('.pp-hero h1')[0]), { yPercent: -70, opacity: 0, stagger: 0.06, duration: 0.7, ease: 'power2.in' }, 0)
      .to(q('.pp-hero > :not(h1)'), { y: -24, opacity: 0, duration: 0.6, ease: 'power2.in' }, 0)
    // The headline arrives, then shrinks into the bar as the thread stands up.
      .to(chars(head, { opacity: 0, yPercent: 45 }), { opacity: 1, yPercent: 0, stagger: 0.035, duration: 0.45 }, 0.75)
      .to(q('.pp-kick'), { opacity: 1, duration: 0.4 }, 0.8)
      .to(obj, { rotationX: 0, y: 0, scale: 1, opacity: 1, duration: 1.4, ease: 'power2.inOut' }, 1.5)
      .to(head, { x: dock.x, y: dock.y, scale: dock.scale, duration: 1.4, ease: 'power2.inOut' }, 1.5)
    // Beat 1: the question.
      .to(chars(q('.pi-title')[0]), { opacity: 1, duration: 0.02, stagger: 0.022 }, 2.8)
      .to(q('.pi-labels > *'), { opacity: 1, duration: 0.3, stagger: 0.12 }, 3.5)
    // Beat 2: it keeps coming up, and people search for it.
      .to(q('.pi-comment'), { opacity: 1, x: 0, duration: 0.45, stagger: 0.28 }, 4.7)
      .to(q('.pi-dup'), { opacity: 1, scale: 1, duration: 0.3, stagger: 0.28, ease: 'back.out(2)' }, 5.0)
      .to(q('.pi-source'), { opacity: 1, duration: 0.4 }, 5.5)
      .to(q('.pi-demand svg'), { opacity: 1, duration: 0.3 }, 5.8)
      .to(q('.pi-demand i'), { scaleY: 1, duration: 0.4, stagger: { each: 0.06, from: 'center' } }, 5.9)
    // Beat 3: one question, one page.
      .to(q('.pi-linked'), { opacity: 1, y: 0, duration: 0.4 }, 7.2)
    // The thread leaves upward.
      .to([head, q('.pp-kick')], { opacity: 0, duration: 0.5, ease: 'power2.in' }, 9.0)
      .to(obj, gone, 9.0);
    captions(tl, scene, [3.0, 4.7, 7.0, 9.2]);
    tl.set({}, {}, 10.2);
  })();

  // ---- The repro ---------------------------------------------------------------
  (function () {
    var scene = document.getElementById('repro');
    if (!scene) return;
    var q = function (selector) { return scene.querySelectorAll(selector); };
    var obj = q('.pp-obj')[0], head = q('.pp-head')[0], dock = docking(scene);
    var lines = q('.pt-line'), tl = scrubbed(scene);

    gsap.set(q('.pp-col'), { visibility: 'visible' });
    gsap.set(obj, Object.assign({ opacity: 0 }, lying));
    gsap.set([q('.pp-kick'), q('.pt-title')], { opacity: 0 });
    gsap.set(q('.pt-out'), { opacity: 0, y: 6 });

    // A command is typed one character at a time; its result lands when it finishes.
    function run(command, result, at) {
      var typed = chars(command.querySelector('.pt-type'));
      tl.to(typed, { opacity: 1, duration: 0.01, stagger: 0.5 / typed.length }, at);
      if (result) tl.to(result, { opacity: 1, y: 0, duration: 0.3 }, at + 0.75);
    }

    tl.to(chars(head, { opacity: 0, yPercent: 45 }), { opacity: 1, yPercent: 0, stagger: 0.035, duration: 0.45 }, 0.1)
      .to(q('.pp-kick'), { opacity: 1, duration: 0.4 }, 0.15)
      .to(obj, { rotationX: 0, y: 0, scale: 1, opacity: 1, duration: 1.3, ease: 'power2.inOut' }, 0.8)
      .to(head, { x: dock.x, y: dock.y, scale: dock.scale, duration: 1.3, ease: 'power2.inOut' }, 0.8)
      .to(q('.pt-title'), { opacity: 1, duration: 0.4 }, 2.0);
    // Beat 1: install, and the happy path passes.
    run(lines[0], null, 2.3);
    run(lines[1], lines[2], 3.0);
    // Beat 2: the edge case. Nothing throws; the form is just wrong.
    run(lines[3], lines[4], 4.8);
    tl.to(obj, { keyframes: { x: [0, -10, 10, -6, 6, 0] }, duration: 0.5, ease: 'none' }, 5.6);
    // Beat 3: keep what ran.
    run(lines[5], lines[6], 6.9);
    tl.to([lines[3], lines[4]], { opacity: 0.4, duration: 0.4 }, 7.7)
      .to([head, q('.pp-kick')], { opacity: 0, duration: 0.5, ease: 'power2.in' }, 9.0)
      .to(obj, gone, 9.0);
    captions(tl, scene, [2.3, 4.6, 6.8, 9.2]);
    tl.set({}, {}, 10.2);
  })();

  root.setAttribute('data-pp-ready', '');
  ScrollTrigger.refresh();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { ScrollTrigger.refresh(); });
  window.addEventListener('load', function () { ScrollTrigger.refresh(); });
})();
