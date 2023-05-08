import { resolve, dirname, basename } from 'path';
import { writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { globSync } from 'glob';
import { createRequire } from 'module';
import { flattenLocales, unflattenLocales } from './utils.js';

const require = createRequire(import.meta.url);

const modulePaths = globSync(
  resolve(
    dirname(fileURLToPath(import.meta.url)),
    '../../src/plugins/i18n/locales/*.json'
  )
);

const locales = modulePaths.reduce(
  (acc, path) => ({
    ...acc,
    [basename(path).replace('.json', '')]: require(resolve(path)),
  }),
  {}
);

// Flatten all locales.
const flattened = flattenLocales(locales);

// List keys in the default 'en' locale and their values
// missing from each flattened locale.
const missingKeys = Object.entries(flattened).reduce(
  (acc, [locale, data]) => ({
    ...acc,
    [locale]: Object.keys(flattened.en).reduce((acc, key) => {
      if (!Object.keys(data).includes(key)) {
        return {
          ...acc,
          [key]: `${flattened.en[key]} <${locale.toLocaleUpperCase()}>`,
        };
      }
      return acc;
    }, {}),
  }),
  {}
);

console.log('Missing i18n keys:', missingKeys);

// Add missing keys and their values into flattened locales.
const fixed = Object.entries(flattened).reduce(
  (acc, [locale, data]) => ({
    ...acc,
    [locale]: {
      ...data,
      ...missingKeys[locale],
    },
  }),
  {}
);

// Unflatten fixed locales.
const unflattened = unflattenLocales(fixed);

// Write fixed locales to disk.
Object.entries(unflattened).forEach(([locale, data]) =>
  writeFileSync(
    resolve(
      dirname(fileURLToPath(import.meta.url)),
      `../../src/plugins/i18n/locales/${locale}.json`
    ),
    JSON.stringify(data, null, 2)
  )
);
