import { createI18n } from 'vue-i18n';

// The Locale message resources
function loadLocaleMessages() {
  // Load messages from any json files in the locales folder
  const modules = import.meta.glob('./locales/*.json');
  const messages: any = {};
  for (const path in modules) {
    // For each file found, build the message object
    // with the file NAME as the top level key
    if (modules.path) {
      modules[path]().then((mod: any) => {
        const matches = path.match(/[ \w-]+?(?=\.)/i);
        if (matches && matches.length) {
          messages[matches[0]] = mod;
        }
      });
    }
  }
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
