import { flushPromises, mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test } from 'vitest';

import EditConnection from '@/components/connections/editConnection/EditConnection.vue';

const mountEditConnection = () =>
  mount(EditConnection, {
    props: {
      connectionId: 'test-connection-id',
    },
    global: {
      plugins: [PrimeVue],
      stubs: ['Dialog'],
    },
  });

describe('EditConnection', () => {
  test('mount matches expected components with modal closed', async () => {
    const wrapper = mountEditConnection();

    wrapper.getComponent({ name: 'Button' });
    expect(wrapper.getComponent({ name: 'Dialog' }).attributes().visible).toBe(
      'false'
    );
  });

  test('modal becomes visible on button click', async () => {
    const wrapper = mountEditConnection();

    await wrapper.getComponent({ name: 'Button' }).trigger('click');
    expect(wrapper.getComponent({ name: 'Dialog' }).attributes().visible).toBe(
      'true'
    );
  });
});
