import { flushPromises, mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test } from 'vitest';

import DidExchange from '@/components/connections/didExchange/DidExchange.vue';

const mountDidExchange = () =>
  mount(DidExchange, {
    global: {
      plugins: [PrimeVue],
      stubs: ['Dialog'],
    },
  });

describe('DidExchange', () => {
  test('mount has expected components with modal closed', async () => {
    const wrapper = mountDidExchange();

    wrapper.getComponent({ name: 'Button' });
    expect(wrapper.getComponent({ name: 'Dialog' }).attributes().visible).toBe(
      'false'
    );
  });

  test('modal opens on button click', async () => {
    const wrapper = mountDidExchange();

    wrapper.getComponent({ name: 'Button' }).trigger('click');
    await flushPromises();
    expect(wrapper.getComponent({ name: 'Dialog' }).attributes().visible).toBe(
      'true'
    );
  });
});
