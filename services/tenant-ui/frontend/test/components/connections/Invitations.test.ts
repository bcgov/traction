import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test } from 'vitest';

import Invitations from '@/components/connections/Invitations.vue';

const mountInvitations = () =>
  mount(Invitations, {
    global: {
      plugins: [PrimeVue],
    },
  });

describe('Invitations', () => {
  test('mount renders with expected components', async () => {
    const wrapper = mountInvitations();

    wrapper.getComponent({ name: 'DataTable' });
    expect(wrapper.findAllComponents({ name: 'CreateContact' })).toHaveLength(
      2
    );
    wrapper.getComponent({ name: 'InputText' });
    wrapper.getComponent({ name: 'Button', props: { icon: 'pi pi-refresh' } });
    wrapper.getComponent({ name: 'VirtualScroller' });
    wrapper.getComponent({ name: 'Paginator' });
  });
});
