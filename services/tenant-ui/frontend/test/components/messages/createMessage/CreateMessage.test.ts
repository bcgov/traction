import { flushPromises, mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test } from 'vitest';

import CreateMessage from '@/components/messages/createMessage/CreateMessage.vue';

const mountCreateMessage = () =>
  mount(CreateMessage, {
    global: {
      plugins: [PrimeVue],
      stubs: ['Dialog'],
    },
  });

describe('CreateMessage', () => {
  test('mount matches expected values', async () => {
    const wrapper = mountCreateMessage();

    wrapper.getComponent({ name: 'Button', props: { icon: 'pi pi-envelope' } });
    expect(wrapper.getComponent({ name: 'Dialog' }).attributes().visible).toBe(
      'false'
    );
    expect(wrapper.getComponent({ name: 'Dialog' }).attributes().modal).toBe(
      'true'
    );
  });

  test('clicking span sets dialog to visible', async () => {
    const wrapper = mountCreateMessage();

    await wrapper
      .getComponent({ name: 'Button', props: { icon: 'pi pi-envelope' } })
      .trigger('click');

    expect(wrapper.getComponent({ name: 'Dialog' }).attributes().visible).toBe(
      'true'
    );
  });
});
