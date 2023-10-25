import { createTestingPinia } from '@pinia/testing';
import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import ConfirmationService from 'primevue/confirmationservice';
import { describe, expect, test } from 'vitest';

import Invitations from '@/components/connections/Invitations.vue';

const mountInvitations = () =>
  mount(Invitations, {
    global: {
      plugins: [PrimeVue, createTestingPinia(), ConfirmationService],
    },
  });

describe('Invitations', () => {
  test('mount renders with expected components', async () => {
    const wrapper = mountInvitations();

    wrapper.getComponent({ name: 'DataTable' });
    expect(
      wrapper.findAllComponents({ name: 'CreateConnection' })
    ).toHaveLength(1);
  });

  test('table body is rendered with expected values', async () => {
    const wrapper = mountInvitations();
    const expectedTexts = ['', 'test.alias', 'once', 'connections/1.0'];

    // td is an expected text or valid date
    wrapper.findAll('tbody td').forEach((td) => {
      const text = td.text();
      expect(expectedTexts.includes(text) || !isNaN(Date.parse(text))).toBe(
        true
      );
    });
  });
});
