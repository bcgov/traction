import { flushPromises, mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test } from 'vitest';

import EditContact from '@/components/connections/editContact/EditContact.vue';

const mountEditContact = () =>
  mount(EditContact, {
    props: {
      connectionId: 'test-connection-id',
    },
    global: {
      plugins: [PrimeVue],
      stubs: ['Dialog'],
    },
  });

describe('EditContact', () => {
  test('mount matches expected components with modal closed', async () => {
    const wrapper = mountEditContact();

    wrapper.getComponent({ name: 'Button' });
    expect(wrapper.getComponent({ name: 'Dialog' }).vm.visible).toBe(false);
  });

  test('modal becomes visible on button click', async () => {
    const wrapper = mountEditContact();

    await wrapper.getComponent({ name: 'Button' }).trigger('click');
    expect(wrapper.getComponent({ name: 'Dialog' }).vm.visible).toBe(true);
  });
});
