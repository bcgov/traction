import { createTestingPinia } from '@pinia/testing';
import { flushPromises, mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test } from 'vitest';

import MessageContact from '@/components/connections/messageContact/MessageContact.vue';

const mountMessageContact = () =>
  mount(MessageContact, {
    props: {
      connectionId: 'test-connection-id',
      connectionName: 'test-connection-name',
    },
    global: {
      plugins: [PrimeVue, createTestingPinia()],
      stubs: ['Sidebar'],
    },
  });

describe('MessageContact', () => {
  test('mount matches expected components with sidebar closed', async () => {
    const wrapper = mountMessageContact();

    wrapper.getComponent({ name: 'Button', props: { icon: 'pi pi-comments' } });
    const sidebar = wrapper.getComponent({ name: 'Sidebar' });
    expect(sidebar.vm.visible).toBe(false);
    expect(sidebar.vm.position).toBe('right');
  });

  test('sidebar opens on button click', async () => {
    const wrapper = mountMessageContact();

    await wrapper
      .getComponent({ name: 'Button', props: { icon: 'pi pi-comments' } })
      .trigger('click');

    const sidebar = wrapper.getComponent({ name: 'Sidebar' });
    expect(sidebar.vm.visible).toBe(true);
  });
});
