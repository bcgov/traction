import { createTestingPinia } from '@pinia/testing';
import { mount } from '@vue/test-utils';
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

    const expectedTexts = ['Tenant', 'June 23 2023, 3:24:38 PM'];

    // Tests that all expected texts are present in component
    expect(
      expectedTexts.every((c) =>
        wrapper
          .findAll('tbody td')
          .map((td) => td.text())
          .includes(c)
      )
    ).toBe(true);
  });
});
