import { createTestingPinia } from '@pinia/testing';
import { flushPromises, mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test } from 'vitest';

import Tenants from '@/components/innkeeper/tenants/Tenants.vue';

const mountTenants = () =>
  mount(Tenants, {
    global: {
      plugins: [PrimeVue, createTestingPinia()],
    },
  });

describe('InnkeeperLogin', async () => {
  test('formattedTenants formats and the data renders in table body', async () => {
    const wrapper = mountTenants();
    const expectedTexts = ['', 'Tenant'];

    // td is an expected text or valid date
    wrapper.findAll('tbody td').forEach((td) => {
      const text = td.text();
      expect(expectedTexts.includes(text) || !isNaN(Date.parse(text))).toBe(
        true
      );
    });
  });
});
