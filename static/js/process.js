/* Process page (/technical-writing-process/). Vanilla, no dependencies.

   The page is complete without this file. A one-line script in the page head adds
   .pp-live when motion is welcome, and .pp-io as well when the browser has no
   scroll-driven animations. With scroll timelines process.css does all of the motion.
   This file adds:
   1. the rail's mark on the stage on screen;
   2. the step each figure has reached, which counts numbers up to their real value
      the first time they appear;
   3. under .pp-io, which figure is on stage, so process.css can play the same scenes
      as transitions.

   Cloudflare Rocket Loader runs this after load, so a reader may already be mid-page;
   everything here is computed from where the page is, never assumed to start at the top. */
(function () {
  'use strict';

  var root = document.documentElement;
  var scenes = Array.prototype.slice.call(document.querySelectorAll('.pp-scene'));
  var figures = Array.prototype.slice.call(document.querySelectorAll('[data-figure]'));
  if (!scenes.length || !('IntersectionObserver' in window)) return;

  function watch(observer, nodes) {
    Array.prototype.forEach.call(nodes, function (node) { observer.observe(node); });
    return observer;
  }

  // 1. Rail. A scene is current while it covers the line 45% down the window.
  var links = {};
  Array.prototype.forEach.call(document.querySelectorAll('.pp-rail-link'), function (link) {
    links[link.getAttribute('href').slice(1)] = link;
  });
  watch(new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      var link = links[entry.target.id];
      if (!link) return;
      if (entry.isIntersecting) link.setAttribute('aria-current', 'step');
      else link.removeAttribute('aria-current');
    });
  }, { rootMargin: '-45% 0px -55% 0px' }), scenes);

  if (!root.classList.contains('pp-live')) return;

  // A number counts up once, and only if it was off screen when this file ran.
  function countUp(element) {
    if (element.hasAttribute('data-counted')) return;
    element.setAttribute('data-counted', '');
    var final = element.textContent;
    var match = /^([\d,]+)(.*)$/.exec(final);
    if (!match) return;
    var target = parseInt(match[1].replace(/,/g, ''), 10);
    var grouped = match[1].indexOf(',') !== -1;
    var started = null;
    function frame(now) {
      if (started === null) started = now;
      var t = Math.min((now - started) / 900, 1);
      var value = Math.round(target * (1 - Math.pow(1 - t, 3)));
      element.textContent = t < 1 ? (grouped ? value.toLocaleString('en-US') : String(value)) + match[2] : final;
      if (t < 1) window.requestAnimationFrame(frame);
    }
    window.requestAnimationFrame(frame);
  }

  // 2 and 3. A scene is on stage once its top is above the line 85% down the window;
  // a beat counts once its top is above the line 75% down.
  var SCENE_LINE = 0.85;
  var BEAT_LINE = 0.75;
  var first = true;

  function update() {
    var height = window.innerHeight;
    var current = 0;
    scenes.forEach(function (scene, index) {
      if (scene.getBoundingClientRect().top < height * SCENE_LINE) current = index;
    });
    figures.forEach(function (figure, index) {
      var step = 0;
      if (index < current) step = 3;
      else if (index === current) {
        Array.prototype.forEach.call(scenes[index].querySelectorAll('.pp-beat'), function (beat) {
          if (beat.getBoundingClientRect().top < height * BEAT_LINE) step += 1;
        });
      }
      figure.classList.toggle('is-before', index > current);
      figure.classList.toggle('is-after', index < current);
      if (figure.getAttribute('data-step') === String(step)) return;
      figure.setAttribute('data-step', step);
      Array.prototype.forEach.call(figure.querySelectorAll('[data-count]'), function (number) {
        var part = number.closest('.s2, .s3');
        var needs = !part ? 1 : part.classList.contains('s3') ? 3 : 2;
        if (step < needs) return;
        if (first) number.setAttribute('data-counted', '');
        else countUp(number);
      });
    });
    first = false;
  }

  update();
  watch(new IntersectionObserver(update, { rootMargin: '0px 0px -' + Math.round((1 - SCENE_LINE) * 100) + '% 0px' }), scenes);
  watch(new IntersectionObserver(update, { rootMargin: '0px 0px -' + Math.round((1 - BEAT_LINE) * 100) + '% 0px' }),
    document.querySelectorAll('.pp-beat'));

  // The results: count each headline figure and, without scroll timelines, grow its bar.
  var results = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      if (entry.target.hasAttribute('data-count')) countUp(entry.target);
      else entry.target.classList.add('is-in');
      results.unobserve(entry.target);
    });
  }, { threshold: 0.6 });
  Array.prototype.forEach.call(document.querySelectorAll('.pp-result-num, .pv'), function (node) {
    var box = node.getBoundingClientRect();
    // Already on screen when this file ran: leave it finished.
    if (box.bottom > 0 && box.top < window.innerHeight) node.classList.add('is-in');
    else results.observe(node);
  });
})();
