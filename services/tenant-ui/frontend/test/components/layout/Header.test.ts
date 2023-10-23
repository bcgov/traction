import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test } from 'vitest';
import { createTestingPinia } from '@pinia/testing';

import Header from '@/components/layout/Header.vue';

describe('Header', async () => {
  test('mount matches snapshot with expected values', async () => {
    const wrapper = mount(Header, {
      global: {
        plugins: [PrimeVue, createTestingPinia()],
        stubs: [
          'router-link',
          'ProfileButton',
          'LocaleSwitcher',
          'SessionTimer',
        ],
      },
    });

    expect(wrapper.html()).toMatchSnapshot();
  });
});
