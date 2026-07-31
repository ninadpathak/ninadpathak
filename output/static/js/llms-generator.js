(function () {
  'use strict';

  var form = document.getElementById('llmsGeneratorForm');
  if (!form) return;

  var fields = {
    name: document.getElementById('llmsSiteName'),
    url: document.getElementById('llmsSiteUrl'),
    description: document.getElementById('llmsSiteDescription'),
    primary: document.getElementById('llmsPrimaryLinks'),
    optional: document.getElementById('llmsOptionalLinks')
  };
  var output = document.getElementById('llmsOutput');
  var status = document.getElementById('llmsStatus');
  var validation = document.getElementById('llmsValidation');
  var copyButton = document.getElementById('llmsCopy');
  var downloadButton = document.getElementById('llmsDownload');
  var sampleButton = document.getElementById('llmsLoadSample');
  var clearButton = document.getElementById('llmsClear');
  var generatedText = '';

  function cleanText(value) {
    return value.trim().replace(/\s+/g, ' ');
  }

  function normalizeBaseUrl(value) {
    var parsed = new URL(value);
    if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
      throw new Error('Use an http:// or https:// website URL.');
    }
    parsed.hash = '';
    parsed.search = '';
    return parsed.toString().replace(/\/$/, '');
  }

  function normalizePageUrl(value, baseUrl) {
    var parsed = new URL(value.trim(), baseUrl + '/');
    if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
      throw new Error('Every page URL must use http:// or https://.');
    }
    parsed.hash = '';
    return parsed.toString();
  }

  function parseLinks(raw, baseUrl, label) {
    if (!raw.trim()) return [];
    return raw.split('\n').map(function (line, index) {
      var parts = line.split('|').map(function (part) { return cleanText(part); });
      if (parts.length < 2 || !parts[0] || !parts[1]) {
        throw new Error(label + ' line ' + (index + 1) + ' needs at least a title and URL separated by |.');
      }
      return {
        title: parts[0],
        url: normalizePageUrl(parts[1], baseUrl),
        description: parts.slice(2).join(' | ')
      };
    });
  }

  function renderSection(lines, heading, links) {
    if (!links.length) return;
    lines.push('## ' + heading, '');
    links.forEach(function (link) {
      var item = '- [' + link.title + '](' + link.url + ')';
      if (link.description) item += ': ' + link.description;
      lines.push(item);
    });
    lines.push('');
  }

  function showError(message) {
    status.textContent = message;
    status.className = 'llms-status llms-status-error';
    validation.innerHTML = '<span class="llms-validation-dot" aria-hidden="true"></span> Check the highlighted input';
    validation.className = 'llms-validation llms-validation-error';
  }

  function showSuccess(linkCount) {
    status.textContent = 'Generated ' + linkCount + ' canonical page link' + (linkCount === 1 ? '' : 's') + '.';
    status.className = 'llms-status llms-status-success';
    validation.innerHTML = '<span class="llms-validation-dot" aria-hidden="true"></span> Format checks passed';
    validation.className = 'llms-validation llms-validation-success';
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    status.textContent = '';

    try {
      var siteName = cleanText(fields.name.value);
      var siteDescription = cleanText(fields.description.value);
      var baseUrl = normalizeBaseUrl(fields.url.value);
      var primaryLinks = parseLinks(fields.primary.value, baseUrl, 'Important pages');
      var optionalLinks = parseLinks(fields.optional.value, baseUrl, 'Optional pages');
      var allLinks = primaryLinks.concat(optionalLinks);

      if (!siteName || !siteDescription || !primaryLinks.length) {
        throw new Error('Add a website name, summary, and at least one important page.');
      }

      var seen = new Set();
      allLinks.forEach(function (link) {
        if (seen.has(link.url)) throw new Error('Remove the duplicate URL: ' + link.url);
        seen.add(link.url);
      });

      var lines = ['# ' + siteName, '', '> ' + siteDescription, ''];
      renderSection(lines, 'Important pages', primaryLinks);
      renderSection(lines, 'Optional', optionalLinks);
      generatedText = lines.join('\n').trim() + '\n';
      output.textContent = generatedText;
      copyButton.disabled = false;
      downloadButton.disabled = false;
      showSuccess(allLinks.length);
    } catch (error) {
      generatedText = '';
      copyButton.disabled = true;
      downloadButton.disabled = true;
      showError(error.message);
    }
  });

  sampleButton.addEventListener('click', function () {
    fields.name.value = 'Acme Developer Docs';
    fields.url.value = 'https://docs.example.com';
    fields.description.value = 'Developer documentation for the Acme API, SDKs, and command-line tools.';
    fields.primary.value = [
      'Quickstart | /quickstart/ | Install the SDK and make your first API request.',
      'API Reference | /api/ | Endpoints, authentication, parameters, and response schemas.',
      'SDK Guides | /sdks/ | Language-specific installation and usage guides.'
    ].join('\n');
    fields.optional.value = 'Changelog | /changelog/ | Product, SDK, and API changes.';
    form.requestSubmit();
  });

  clearButton.addEventListener('click', function () {
    window.setTimeout(function () {
      generatedText = '';
      output.textContent = 'Your generated file will appear here.';
      status.textContent = '';
      status.className = 'llms-status';
      validation.innerHTML = '<span class="llms-validation-dot" aria-hidden="true"></span> Waiting for input';
      validation.className = 'llms-validation';
      copyButton.disabled = true;
      downloadButton.disabled = true;
    }, 0);
  });

  copyButton.addEventListener('click', function () {
    if (!generatedText) return;
    navigator.clipboard.writeText(generatedText).then(function () {
      copyButton.textContent = 'copied';
      window.setTimeout(function () { copyButton.textContent = 'copy'; }, 1500);
    }).catch(function () {
      showError('The browser blocked clipboard access. Select and copy the preview manually.');
    });
  });

  downloadButton.addEventListener('click', function () {
    if (!generatedText) return;
    var blob = new Blob([generatedText], { type: 'text/plain;charset=utf-8' });
    var url = URL.createObjectURL(blob);
    var link = document.createElement('a');
    link.href = url;
    link.download = 'llms.txt';
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  });
})();
