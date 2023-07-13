import { createTestingPinia } from '@pinia/testing';
import { shallowMount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test } from 'vitest';

import InnkeeperLogin from '@/components/innkeeper/InnkeeperLogin.vue';

import { configStore } from '../../__mocks__/store';

const mountLogin = () =>
  shallowMount(InnkeeperLogin, {
    global: {
      plugins: [PrimeVue, createTestingPinia()],
    },
  });

describe('InnkeeperLogin', async () => {
  test('renders InnkeeperLoginForm when showInnkeeperAdminLogin true', async () => {
    const wrapper = mountLogin();
    wrapper.getComponent({ name: 'InnkeeperLoginForm' });
  });

  test('does not render InnkeeperLoginForm when showInnkeeperAdminLogin false', async () => {
    configStore.config.frontend.showInnkeeperAdminLogin = false;
    const wrapper = mountLogin();

    expect(
      wrapper.findComponent({ name: 'InnkeeperLoginForm' }).exists()
    ).toBeFalsy();
  });

  test('InnkeeperLoginOidc shows when oidc active ', async () => {
    configStore.config.frontend.oidc.active = true;
    const wrapper = mountLogin();

    wrapper.getComponent({ name: 'InnkeeperLoginOidc' });
  });
});
