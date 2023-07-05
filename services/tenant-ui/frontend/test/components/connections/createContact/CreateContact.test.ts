import { flushPromises, mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test } from 'vitest';

import CreateContact from '@/components/connections/createContact/CreateContact.vue';

const mountCreateContact = () =>
  mount(CreateContact, {
    props: {
      multi: true,
    },
    global: {
      plugins: [PrimeVue],
      stubs: ['Dialog'],
    },
  });

describe('CreateContact', async () => {
  test('renders as with expected ', async () => {
    const wrapper = mountCreateContact();

    wrapper.getComponent({ name: 'Button' });

    expect(wrapper.getComponent({ name: 'Dialog' }).vm.visible).toBe(false);
  });

  test('button click opens modal', async () => {
    const wrapper = mountCreateContact();

    wrapper.getComponent({ name: 'Button' }).trigger('click');
    await flushPromises();
    expect(wrapper.getComponent({ name: 'Dialog' }).vm.visible).toBe(true);
  });
});
