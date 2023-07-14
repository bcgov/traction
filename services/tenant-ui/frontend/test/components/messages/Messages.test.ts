import { createTestingPinia } from '@pinia/testing';
import { flushPromises, mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test } from 'vitest';

import Messages from '@/components/messages/Messages.vue';

const mountMessages = () =>
  mount(Messages, {
    global: {
      plugins: [PrimeVue, createTestingPinia()],
    },
  });

describe('Messages', async () => {
  test('mount has expected components', () => {
    const wrapper = mountMessages();
    wrapper.getComponent({ name: 'DataTable' });
    wrapper.getComponent({ name: 'CreateMessage' });
  });

  test('table body is rendered with expected values', async () => {
    const wrapper = mountMessages();
    await flushPromises();

    const expectedTexts = ['test-name', 'sent', 'test-content'];

    // td is an expected text or valid date
    wrapper.findAll('tbody td').forEach((td) => {
      const text = td.text();
      expect(expectedTexts.includes(text) || !isNaN(Date.parse(text))).toBe(
        true
      );
    });
  });
});
