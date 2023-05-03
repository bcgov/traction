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

// Sort flattened keys alphabetically for each locale.
const sorted = Object.entries(flattened).reduce(
  (acc, [locale, data]) => ({
    ...acc,
    [locale]: Object.fromEntries(
      Object.entries(data).sort(([a], [b]) => a.localeCompare(b))
    ),
  }),
  {}
);

// Unflatten sorted locales.
const unflattened = unflattenLocales(sorted);

// Write sorted locales to disk.
Object.entries(unflattened).forEach(([locale, data]) => {
  writeFileSync(
    resolve(
      dirname(fileURLToPath(import.meta.url)),
      `../../src/plugins/i18n/locales/${locale}.json`
    ),
    JSON.stringify(data, null, 2)
  );
});
