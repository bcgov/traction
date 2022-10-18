import { createI18n } from 'vue-i18n';

// The Locale message resources
// TODO: This should probably be reorganized into JSON files and set up in this method instead
// but how we want to organize our languages is coming after this proof of concept so TBD
// Probably see https://vue-i18n.intlify.dev/guide/advanced/optimization.html#how-to-configure
function loadLocaleMessages() {
  // one json file per language probably best in the future
  const messages = {
    en: {
      structure: {
        greeting: 'Powered by Traction',
        dashboard: 'Dashboard',
        contacts: 'Contacts',
      },
    },
    fr: {
      structure: {
        greeting: 'Propulsé par Traction',
        dashboard: 'Dashboard <FR>',
      },
    },
  };
  return messages;
}

// locale and fallback could be made configurable values later
export default createI18n({
  legacy: false,
  globalInjection: true,
  locale: 'en',
  fallbackLocale: 'en',
  messages: loadLocaleMessages(),
});
