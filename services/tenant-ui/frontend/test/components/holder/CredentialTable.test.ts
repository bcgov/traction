import { createTestingPinia } from '@pinia/testing';
import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import ConfirmationService from 'primevue/confirmationservice';
import { describe, expect, test, vi } from 'vitest';

import CredentialsTable from '@/components/holder/CredentialsTable.vue';
import { connectionStore, holderStore } from '../../../test/__mocks__/store';

// Need to override global mocks that use holder store. Same function names cause conflicts.
// Consider refactoring to use functions in issuer and verifier stores.
vi.mock('pinia', async () => {
  const pinia = await vi.importActual<typeof import('pinia')>('pinia');

  return {
    ...pinia,
    storeToRefs: vi.fn(() => Object.assign(connectionStore, holderStore)),
  };
});

vi.mock('@/store', () => ({
  useConnectionStore: vi.fn(() => connectionStore),
  useHolderStore: vi.fn(() => holderStore),
}));

const mountCredentialsTable = () =>
  mount(CredentialsTable, {
    global: {
      plugins: [PrimeVue, createTestingPinia(), ConfirmationService],
    },
  });

describe('CredentialsTable', () => {
  test('mount has expected components', async () => {
    const wrapper = mountCredentialsTable();

    wrapper.getComponent({ name: 'DataTable' });
  });

  test('table body is rendered with expected values', async () => {
    const wrapper = mountCredentialsTable();
    const expectedTexts = [
      '',
      'test-name',
      'test-cred_def_id',
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
