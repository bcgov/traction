import { flushPromises, mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test } from 'vitest';

import AcceptInvitation from '@/components/connections/acceptInvitation/AcceptInvitation.vue';

const mountAcceptInvitation = () =>
  mount(AcceptInvitation, {
    global: {
      plugins: [PrimeVue],
      stubs: ['Dialog'],
    },
  });

describe('AcceptInvitation', () => {
  test('mount has expected components with dialog not visible', async () => {
    const wrapper = mountAcceptInvitation();

    wrapper.getComponent({ name: 'Button' });
    expect(wrapper.getComponent({ name: 'Dialog' }).attributes().visible).toBe(
      'false'
    );
  });

  test('dialog becomes visible on button click', async () => {
    const wrapper = mountAcceptInvitation();

    await wrapper.getComponent({ name: 'Button' }).trigger('click');
    expect(wrapper.getComponent({ name: 'Dialog' }).attributes().visible).toBe(
      'true'
    );
  });
});
