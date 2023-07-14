import { createTestingPinia } from '@pinia/testing';
import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import ConfirmationService from 'primevue/confirmationservice';
import { describe, expect, test } from 'vitest';

import IssuedCredentials from '@/components/issuance/IssuedCredentials.vue';

const mountIssuedCredentials = () =>
  mount(IssuedCredentials, {
    global: {
      plugins: [PrimeVue, createTestingPinia(), ConfirmationService],
    },
  });

describe('IssuedCredentials', () => {
  test('mount has expected components', async () => {
    const wrapper = mountIssuedCredentials();

    wrapper.getComponent({ name: 'DataTable' });
    wrapper.getComponent({ name: 'OfferCredential' });
  });

  test('table body is rendered with expected values', async () => {
    const wrapper = mountIssuedCredentials();
    const expectedTexts = [
      '',
      'test-cred_def_id',
      'test-name',
      'credential_acked',
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
