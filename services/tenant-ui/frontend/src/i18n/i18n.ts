import { createI18n } from 'vue-i18n';

// The Locale message resources
// TODO: This should probably be reorganized into JSON files and set up in this method instead
// but how we want to organize our languages is coming after this proof of concept so TBD
// Probably see https://vue-i18n.intlify.dev/guide/advanced/optimization.html#how-to-configure
function loadLocaleMessages() {
  // one json file per language probably best in the future
  const messages = {
    en: {
      home: {
        greeting: 'Powered by Traction',
        dashboard: 'Dashboard',
        login: {
          id: 'Wallet ID',
          secret: 'Wallet Secret',
          submit: 'Sign-In',
        },
      },
      user: {
        profile: 'Profile',
        settings: 'Settings',
        logout: 'Logout',
      },
      contact: {
        contacts: 'Contacts',
        create: 'Create Contact',
        accept: 'Accept Invitation',
      },
      issue: {

      },
      verify: {

      },
      holder: {

      },
      schemasCreds: {

      },
      tenants: {

      },
      about: {
        about: 'About'
      }
    },
    fr: {
      home: {
        greeting: 'Propulsé par Traction',
        dashboard: 'Dashboard <FR>',
        login: {
          id: 'Wallet ID <FR>',
          secret: 'Wallet Secret <FR>',
          submit: 'Sign-In <FR>',
        },
      },
      user: {
        profile: 'Profile <FR>',
        settings: 'Settings <FR>',
        logout: 'Logout <FR>',
      },
      contact: {
        contacts: 'Contacts <FR>',
        create: 'Create Contact <FR>',
        accept: 'Accept Invitation <FR>',
      },
    },
    jp: {
      home: {
        greeting: 'トラクションを搭載',
        dashboard: 'Dashboard <JP>',
        login: {
          id: 'Wallet ID <JP>',
          secret: 'Wallet Secret <JP>',
          submit: 'Sign-In <JP>',
        },
      },
      user: {
        profile: 'Profile <JP>',
        settings: 'Settings <JP>',
        logout: 'Logout <JP>',
      },
      contact: {
        contacts: 'Contacts <JP>',
        create: 'Create Contact <JP>',
        accept: 'Accept Invitation <JP>',
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
