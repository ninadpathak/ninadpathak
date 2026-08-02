(function () {
  'use strict';

  var scanForm = document.getElementById('llmsScanForm');
  if (!scanForm) return;

  var scanButton = document.getElementById('llmsScan');
  var sourceUrl = document.getElementById('llmsSiteUrl');
  var status = document.getElementById('llmsStatus');
  var workspace = document.getElementById('llmsWorkspace');
  var pagesContainer = document.getElementById('llmsPages');
  var selectionCount = document.getElementById('llmsSelectionCount');
  var scanSummary = document.getElementById('llmsScanSummary');
  var outputPanel = document.getElementById('llmsOutputPanel');
  var output = document.getElementById('llmsOutput');
  var fields = {
    name: document.getElementById('llmsSiteName'),
    url: document.getElementById('llmsCanonicalUrl'),
    description: document.getElementById('llmsSiteDescription')
  };
  var pages = [];

  function trackEvent(name, parameters) {
    if (typeof window.trackSiteEvent === 'function') window.trackSiteEvent(name, parameters);
  }

  function cleanText(value) {
    return String(value || '').trim().replace(/\s+/g, ' ');
  }

  function normalizeWebsiteUrl(value) {
    var normalized = cleanText(value);
    if (!/^https?:\/\//i.test(normalized)) normalized = 'https://' + normalized;
    var parsed = new URL(normalized);
    if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') throw new Error('Enter a valid website address.');
    return parsed.toString();
  }

  function setStatus(message, kind) {
    status.textContent = message;
    status.className = 'tool-status' + (kind ? ' tool-status-' + kind : '');
  }

  function escapeHtml(value) {
    return String(value || '').replace(/[&<>"']/g, function (character) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[character];
    });
  }

  function defaultSection(page, index) {
    var path = new URL(page.url).pathname.toLowerCase();
    if (/changelog|release|example|blog|article|news/.test(path)) return 'Optional';
    return index < 20 ? 'Important pages' : 'Optional';
  }

  function pageRow(page, index) {
    return [
      '<article class="page-row" data-index="' + index + '">',
      '  <div class="page-row-controls">',
      '    <label class="check-field"><input type="checkbox" data-field="include"' + (page.include ? ' checked' : '') + '> include</label>',
      '    <select data-field="section" aria-label="Section for ' + escapeHtml(page.title) + '">',
      '      <option' + (page.section === 'Important pages' ? ' selected' : '') + '>Important pages</option>',
      '      <option' + (page.section === 'Optional' ? ' selected' : '') + '>Optional</option>',
      '    </select>',
      '    <button type="button" class="text-action" data-remove>remove</button>',
      '  </div>',
      '  <div class="page-row-fields">',
      '    <label class="form-field"><span>Title</span><input data-field="title" value="' + escapeHtml(page.title) + '"></label>',
      '    <label class="form-field"><span>Canonical URL</span><input data-field="url" type="url" value="' + escapeHtml(page.url) + '"></label>',
      '    <label class="form-field page-description"><span>Description</span><textarea data-field="description" rows="2">' + escapeHtml(page.description) + '</textarea></label>',
      '  </div>',
      '</article>'
    ].join('');
  }

  function renderPages() {
    pagesContainer.innerHTML = pages.map(pageRow).join('');
    updateSelectionCount();
  }

  function updateSelectionCount() {
    var selected = pages.filter(function (page) { return page.include; }).length;
    selectionCount.textContent = selected + ' of ' + pages.length + ' page' + (pages.length === 1 ? '' : 's') + ' selected';
  }

  function syncPage(target) {
    var row = target.closest('.page-row');
    if (!row) return;
    var page = pages[Number(row.dataset.index)];
    var field = target.dataset.field;
    if (!page || !field) return;
    page[field] = target.type === 'checkbox' ? target.checked : target.value;
    updateSelectionCount();
  }

  function postJson(payload) {
    return fetch('/api/discover-site', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(payload)
    }).then(function (response) {
      return response.json().then(function (body) {
        if (!response.ok) throw new Error(body.error || 'The website could not be scanned.');
        return body;
      });
    });
  }

  function fetchMetadata(siteUrl, urls) {
    var batches = [];
    for (var index = 0; index < urls.length; index += 20) batches.push(urls.slice(index, index + 20));
    var collected = [];
    return batches.reduce(function (chain, batch, batchIndex) {
      return chain.then(function () {
        setStatus('Reading page metadata: batch ' + (batchIndex + 1) + ' of ' + batches.length + '.', 'loading');
        return postJson({ url: siteUrl, pages: batch });
      }).then(function (result) {
        collected = collected.concat(result.pages);
      });
    }, Promise.resolve()).then(function () { return collected; });
  }

  scanForm.addEventListener('submit', function (event) {
    event.preventDefault();
    var websiteUrl;
    try {
      websiteUrl = normalizeWebsiteUrl(sourceUrl.value);
      sourceUrl.value = websiteUrl.replace(/\/$/, '');
    } catch (error) {
      setStatus(error.message, 'error');
      sourceUrl.focus();
      return;
    }
    scanButton.disabled = true;
    scanButton.textContent = 'Scanning…';
    setStatus('Finding sitemaps and reading page metadata. Keep this tab open.', 'loading');
    workspace.hidden = true;
    outputPanel.hidden = true;

    var discovery;
    postJson({ url: websiteUrl }).then(function (result) {
      discovery = result;
      return fetchMetadata(result.site.url, result.urls);
    }).then(function (metadata) {
      var result = discovery;
      fields.name.value = result.site.name || '';
      fields.url.value = result.site.url || sourceUrl.value;
      fields.description.value = result.site.description || '';
      pages = metadata.map(function (page, index) {
        return {
          include: true,
          section: defaultSection(page, index),
          title: page.title,
          url: page.url,
          description: page.description
        };
      });
      renderPages();
      workspace.hidden = false;
      scanSummary.textContent = pages.length + ' page' + (pages.length === 1 ? '' : 's');
      var detail = result.sitemapFound ? ' from the website sitemap' : ' from the homepage because no sitemap was found';
      if (result.truncated) detail += ' (limited to ' + result.limit + ')';
      setStatus('Found ' + pages.length + ' editable page' + (pages.length === 1 ? '' : 's') + detail + '.', 'success');
      trackEvent('llms_scan_complete', {
        page_count: pages.length,
        sitemap_found: result.sitemapFound,
        truncated: result.truncated
      });
      workspace.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }).catch(function (error) {
      setStatus(error.message + ' Check the URL and confirm the site is publicly reachable.', 'error');
      trackEvent('llms_scan_error');
    }).finally(function () {
      scanButton.disabled = false;
      scanButton.textContent = 'Scan website →';
    });
  });

  pagesContainer.addEventListener('input', function (event) { syncPage(event.target); });
  pagesContainer.addEventListener('change', function (event) { syncPage(event.target); });
  pagesContainer.addEventListener('click', function (event) {
    if (!event.target.matches('[data-remove]')) return;
    var row = event.target.closest('.page-row');
    pages.splice(Number(row.dataset.index), 1);
    renderPages();
  });

  document.getElementById('llmsSelectAll').addEventListener('click', function () {
    pages.forEach(function (page) { page.include = true; });
    renderPages();
  });
  document.getElementById('llmsSelectNone').addEventListener('click', function () {
    pages.forEach(function (page) { page.include = false; });
    renderPages();
  });
  document.getElementById('llmsAddPage').addEventListener('click', function () {
    pages.push({ include: true, section: 'Important pages', title: '', url: fields.url.value + '/', description: '' });
    renderPages();
    pagesContainer.lastElementChild.querySelector('input[data-field="title"]').focus();
  });

  function markdownSection(lines, title, selectedPages) {
    if (!selectedPages.length) return;
    lines.push('## ' + title, '');
    selectedPages.forEach(function (page) {
      var line = '- [' + cleanText(page.title) + '](' + page.url.trim() + ')';
      if (cleanText(page.description)) line += ': ' + cleanText(page.description);
      lines.push(line);
    });
    lines.push('');
  }

  document.getElementById('llmsGenerate').addEventListener('click', function () {
    try {
      var selected = pages.filter(function (page) { return page.include; });
      if (!cleanText(fields.name.value) || !cleanText(fields.description.value)) throw new Error('Add a website name and summary.');
      if (!selected.length) throw new Error('Select at least one page.');
      var seen = new Set();
      selected.forEach(function (page) {
        if (!cleanText(page.title)) throw new Error('Every selected page needs a title.');
        var url = new URL(page.url, fields.url.value).toString();
        if (!/^https?:/.test(url)) throw new Error('Every selected page needs a public HTTP URL.');
        if (seen.has(url)) throw new Error('Remove the duplicate URL: ' + url);
        seen.add(url);
        page.url = url;
      });
      var lines = ['# ' + cleanText(fields.name.value), '', '> ' + cleanText(fields.description.value), ''];
      markdownSection(lines, 'Important pages', selected.filter(function (page) { return page.section === 'Important pages'; }));
      markdownSection(lines, 'Optional', selected.filter(function (page) { return page.section === 'Optional'; }));
      output.value = lines.join('\n').trim() + '\n';
      outputPanel.hidden = false;
      document.getElementById('llmsValidation').textContent = selected.length + ' unique canonical page links. Edit the text directly if you want a final pass.';
      trackEvent('llms_generate', { page_count: selected.length });
      outputPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch (error) {
      setStatus(error.message, 'error');
    }
  });

  document.getElementById('llmsCopy').addEventListener('click', function () {
    navigator.clipboard.writeText(output.value).then(function () {
      setStatus('Copied llms.txt to the clipboard.', 'success');
      trackEvent('llms_copy');
    }).catch(function () { setStatus('Clipboard access was blocked. Select the generated text and copy it manually.', 'error'); });
  });

  document.getElementById('llmsDownload').addEventListener('click', function () {
    trackEvent('llms_download');
    var blobUrl = URL.createObjectURL(new Blob([output.value], { type: 'text/plain;charset=utf-8' }));
    var link = document.createElement('a');
    link.href = blobUrl;
    link.download = 'llms.txt';
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(blobUrl);
  });
})();
