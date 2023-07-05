import { createTestingPinia } from '@pinia/testing';
import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test } from 'vitest';

import Business from '@/components/about/Business.vue';

describe('Business', async () => {
  test('mount matches snapshot with expected values', () => {
    const wrapper = mount(Business, {
      global: {
        plugins: [PrimeVue, createTestingPinia()],
      },
    });

    expect(wrapper.html()).toMatchSnapshot();
  });
});
