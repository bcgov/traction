import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test } from 'vitest';

import Sidebar from '@/components/layout/Sidebar.vue';

describe('Sidebar', async () => {
  test('mount matches snapshot with expected values', () => {
    const wrapper = mount(Sidebar, {
      global: {
        plugins: [PrimeVue],
        stubs: ['router-link'],
      },
    });

    expect(wrapper.html()).toMatchSnapshot();
  });
});
