import { createTestingPinia } from '@pinia/testing';
import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import ConfirmationService from 'primevue/confirmationservice';
import { describe, expect, test } from 'vitest';

import Presentations from '@/components/verifier/Presentations.vue';

const mountPresentations = () =>
  mount(Presentations, {
    global: {
      plugins: [PrimeVue, createTestingPinia(), ConfirmationService],
    },
  });

describe('Presentations', () => {
  test('mount has expected components', async () => {
    const wrapper = mountPresentations();

    wrapper.getComponent({ name: 'DataTable' });
  });

  test('table body is rendered with expected values', async () => {
    const wrapper = mountPresentations();
    const expectedTexts = [
      '',
      'proof-request',
      'prover',
      'test-name',
      'request_received',
    ];

    //td is an expected text or valid date
    wrapper.findAll('tbody td').forEach((td) => {
      const text = td.text();
      expect(expectedTexts.includes(text) || !isNaN(Date.parse(text))).toBe(
        true
      );
    });
  });
});
