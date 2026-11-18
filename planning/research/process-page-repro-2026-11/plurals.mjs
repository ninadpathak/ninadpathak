// The cart line from the example, rendered through react-i18next for one language.
//   node plurals.mjs <lng> [locales dir]
import { readFileSync } from 'node:fs';
import { createElement } from 'react';
import { renderToString } from 'react-dom/server';
import i18next from 'i18next';
import { initReactI18next, useTranslation } from 'react-i18next';

const lng = process.argv[2] || 'en';
const dir = process.argv[3] || 'locales';
const translation = JSON.parse(readFileSync(`${dir}/${lng}.json`, 'utf8'));
await i18next.use(initReactI18next).init({ lng, resources: { [lng]: { translation } }, interpolation: { escapeValue: false } });

function Cart({ count }) {
  const { t } = useTranslation();
  return createElement('p', null, t('items', { count }));
}
const counts = [1, 3, 11];
const rules = new Intl.PluralRules(lng);
let missing = 0;
for (const count of counts) {
  const want = `items_${rules.select(count)}`;
  const { exactUsedKey: usedKey } = i18next.t('items', { count, returnDetails: true });
  const text = renderToString(createElement(Cart, { count })).replace(/<\/?p>/g, '');
  if (usedKey === want) console.log(`ok    count ${count}: ${usedKey}${lng === 'en' ? ` -> "${text}"` : ''}`);
  else { missing += 1; console.log(`wrong count ${count}: wants ${want}, got ${usedKey}`); }
}
process.exit(missing ? 1 : 0);
