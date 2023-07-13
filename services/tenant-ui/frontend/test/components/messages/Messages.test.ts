import { createTestingPinia } from '@pinia/testing';
import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, test } from 'vitest';

import Messages from '@/components/messages/Messages.vue';

describe('Messages', async () => {
  test('mount has expected components', () => {
    const wrapper = mount(Messages, {
      global: {
        plugins: [PrimeVue, createTestingPinia()],
      },
    });
    wrapper.getComponent({ name: 'DataTable' });
    wrapper.getComponent({ name: 'CreateMessage' });
    wrapper.getComponent({ name: 'InputText' });
    wrapper.getComponent({ name: 'Button', props: { icon: 'pi pi-refresh' } });
    wrapper.getComponent({ name: 'VirtualScroller' });
    wrapper.getComponent({ name: 'Paginator' });
  });
});
