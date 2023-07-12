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
  test.todo('formattedTenants formats and the data renders in table body');
});
