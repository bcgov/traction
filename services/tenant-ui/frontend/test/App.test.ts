import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test } from 'vitest';

import { useTenantStore, useTokenStore } from '@/store';
import App from '@/App.vue';

const mountApp = () =>
  mount(App, {
    global: {
      plugins: [PrimeVue],
      stubs: ['router-view'],
    },
  });

describe('App', () => {
  test('document title is set', async () => {
    mountApp();

    expect(document.title).toEqual('Tenant UI');
  });

  test('when app opens without refresh should call clear tenant local storage functions', async () => {
    mountApp();

    expect(useTenantStore().clearTenant).toHaveBeenCalled();
    expect(useTokenStore().clearToken).toHaveBeenCalled();
  });

  test.todo(
    'Should test refresh does not call clear local storage functions (not sure if possible with session storage)'
  );
});
