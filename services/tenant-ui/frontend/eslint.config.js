import globals from 'globals';
import js from '@eslint/js';
import tseslint from 'typescript-eslint';
import pluginVue from 'eslint-plugin-vue';
import eslintConfigPrettier from 'eslint-config-prettier';
import eslintPluginPrettierRecommended from 'eslint-plugin-prettier/recommended';
import intlifyVueI18n from '@intlify/eslint-plugin-vue-i18n';

export default tseslint.config(
  js.configs.recommended,
  ...tseslint.configs.recommended,
  ...pluginVue.configs['flat/recommended'],
  eslintPluginPrettierRecommended,
  {
    ignores: [
      '**/schema.ts',
      '**/dist/**',
      '**/coverage/**',
      '**/node_modules/**',
      '**/src/types/acapyApi/acapyInterface.ts',
    ],
  },
  {
    files: ['**/*.{js,mjs,cjs,vue,ts}'],
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
      },
      parserOptions: {
        parser: tseslint.parser,
        sourceType: 'module',
      },
    },
    settings: {
      'vue-i18n': {
        localeDir: './src/locales/*.json',
        messageSyntaxVersion: '^9.2.2',
      },
    },
    rules: {
      'no-unused-vars': 'off', // VUE rule needs to be off
      '@typescript-eslint/no-unused-vars': [
        'error',
        {
          argsIgnorePattern: '^_',
          varsIgnorePattern: '^_',
          caughtErrorsIgnorePattern: '^_',
        },
      ],
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/ban-types': 'off',
      '@typescript-eslint/no-empty-function': 'off',
      'vue/multi-word-component-names': 'off',
    },
  },
  ...intlifyVueI18n.configs['flat/recommended'],
  eslintConfigPrettier
);
