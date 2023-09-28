import { flatten, unflatten } from 'flat';

// Flatten unflattened locales.
export const flattenLocales = (unflattened) => {
  return Object.entries(unflattened).reduce(
    (acc, [locale, data]) => ({
      ...acc,
      [locale]: flatten(data, { object: true }),
    }),
    {}
  );
};

// Unflatten flattened locales.
export const unflattenLocales = (flattened) => {
  return Object.entries(flattened).reduce(
    (acc, [locale, data]) => ({
      ...acc,
      [locale]: unflatten(data, { object: true }),
    }),
    {}
  );
};
