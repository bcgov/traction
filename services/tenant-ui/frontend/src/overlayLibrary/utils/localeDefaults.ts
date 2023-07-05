/**
 * Determine a fallback or default locale to use based on the overlay object
 * @param { Object } overlayObject the object of translations from the overlay
 * @param { string } locale the selected language locale
 * @returns { string } a locale string
 */
export const localeDefault = (overlayObject: Object, locale: string) => {
  const defaultLocale = 'en-CA';
  try {
    if (locale in overlayObject) {
      // If the object has the locale selected by the switcher, go with that
      return locale;
    }
    // For BC Gov oca repository, default to the CA locale for en and fr
    // This will not be used when a general OCA solution is implemented
    if (['en', 'fr'].includes(locale)) {
      return `${locale}-CA`;
    }
  } catch (error) {
    console.error(error);
  }

  // en-CA as the default if nothing else found
  return defaultLocale;
};
