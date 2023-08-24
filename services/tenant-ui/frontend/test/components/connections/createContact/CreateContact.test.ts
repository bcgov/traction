import { flushPromises, mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test } from 'vitest';

import CreateConnection from '@/components/connections/createConnection/CreateConnection.vue';

const mountCreateConnection = () =>
  mount(CreateConnection, {
    props: {
      multi: true,
    },
    global: {
      plugins: [PrimeVue],
      stubs: ['Dialog'],
    },
  });

describe('CreateConnection', async () => {
  test('renders as with expected ', async () => {
    const wrapper = mountCreateConnection();

    wrapper.getComponent({ name: 'Button' });

    expect(wrapper.getComponent({ name: 'Dialog' }).attributes().visible).toBe(
      'false'
    );
  });

  test('button click opens modal', async () => {
    const wrapper = mountCreateConnection();

    wrapper.getComponent({ name: 'Button' }).trigger('click');
    await flushPromises();
    expect(wrapper.getComponent({ name: 'Dialog' }).attributes().visible).toBe(
      'true'
    );
  });
});
