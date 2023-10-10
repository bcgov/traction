import { createTestingPinia } from '@pinia/testing';
import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import ConfirmationService from 'primevue/confirmationservice';
import { describe, expect, test } from 'vitest';

import CredentialDefinitions from '@/components/issuance/credentialDefinitions/CredentialDefinitions.vue';

import { configStore } from '../../../__mocks__/store';

const mountCredentialDefinitions = () =>
  mount(CredentialDefinitions, {
    global: {
      plugins: [PrimeVue, createTestingPinia(), ConfirmationService],
    },
  });

describe('CredentialDefinitions', () => {
  test('mount has expected components', async () => {
    const wrapper = mountCredentialDefinitions();

    wrapper.getComponent({ name: 'CreateCredentialDefinition' });
  });

  test('mount with showWritableComponents false does not have CreateSchema component', async () => {
    configStore.config.frontend.showWritableComponents = false;
    const wrapper = mountCredentialDefinitions();

    expect(
      wrapper.findComponent({ name: 'CreateCredentialDefinition' }).exists()
    ).toBe(false);
  });
});
