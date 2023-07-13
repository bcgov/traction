import { createTestingPinia } from '@pinia/testing';
import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, test } from 'vitest';

import IssuedCredentials from '@/components/issuance/IssuedCredentials.vue';

const mountIssuedCredentials = () =>
  mount(IssuedCredentials, {
    global: {
      plugins: [PrimeVue, createTestingPinia()],
    },
  });

describe('IssuedCredentials', () => {
  test('mount has expected components', async () => {
    const wrapper = mountIssuedCredentials();

    wrapper.getComponent({ name: 'DataTable' });
    wrapper.getComponent({ name: 'OfferCredential' });
    wrapper.getComponent({ name: 'InputText' });
    wrapper.getComponent({ name: 'Button', props: { icon: 'pi pi-refresh' } });
    wrapper.getComponent({ name: 'VirtualScroller' });
    wrapper.getComponent({ name: 'Paginator' });
  });
});
