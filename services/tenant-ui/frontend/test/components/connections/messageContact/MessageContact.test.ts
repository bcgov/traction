import { createTestingPinia } from '@pinia/testing';
import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test } from 'vitest';

import MessageConnection from '@/components/connections/messageConnection/MessageConnection.vue';

const mountMessageConnection = () =>
  mount(MessageConnection, {
    props: {
      connectionId: 'test-connection-id',
      connectionName: 'test-connection-name',
    },
    global: {
      plugins: [PrimeVue, createTestingPinia()],
      stubs: ['Sidebar'],
    },
  });

describe('MessageConnection', () => {
  test('mount matches expected components with sidebar closed', async () => {
    const wrapper = mountMessageConnection();

    wrapper.getComponent({ name: 'Button', props: { icon: 'pi pi-comments' } });
    const sidebar = wrapper.getComponent({ name: 'Sidebar' });
    expect(sidebar.attributes().visible).toBe('false');
    expect(sidebar.attributes().position).toBe('right');
  });

  test('sidebar opens on button click', async () => {
    const wrapper = mountMessageConnection();

    await wrapper
      .getComponent({ name: 'Button', props: { icon: 'pi pi-comments' } })
      .trigger('click');

    const sidebar = wrapper.getComponent({ name: 'Sidebar' });
    expect(sidebar.attributes().visible).toBe('true');
  });
});
