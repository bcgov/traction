import { resolve, dirname, basename } from 'path';
import { fileURLToPath } from 'url';
import { globSync } from 'glob';
import { createRequire } from 'module';
import { flattenLocales } from './utils.js';

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

// List all values in the flattened 'en' locale that are duplicated and their keys.
const valuesByKey = Object.entries(flattened.en).reduce(
  (acc, [key, value]) => ({
    ...acc,
    [value]: [...(acc[value] || []), key],
  }),
  {}
);

const duplicates = Object.entries(valuesByKey)
  .filter(([_, keys]) => keys.length > 1)
  .reduce(
    (acc, [value, keys]) => ({
      ...acc,
      [value]: keys,
    }),
    {}
  );

console.log('Duplicate i18n values:', duplicates);
console.log(
  'Consider adding these to a common object:',
  Object.keys(duplicates)
);
