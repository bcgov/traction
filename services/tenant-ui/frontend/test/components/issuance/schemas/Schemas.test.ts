import { createTestingPinia } from '@pinia/testing';
import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import ConfirmationService from 'primevue/confirmationservice';
import { describe, expect, test } from 'vitest';

import Schemas from '@/components/issuance/schemas/Schemas.vue';

import { configStore, governanceStore } from '../../../__mocks__/store';

const mountSchemas = () =>
  mount(Schemas, {
    global: {
      plugins: [PrimeVue, createTestingPinia(), ConfirmationService],
      stubs: ['NestedCredentialDefinition'],
    },
  });

describe('Schemas', () => {
  test('mount has expected components', async () => {
    const wrapper = mountSchemas();

    wrapper.getComponent({ name: 'CreateSchema' });
    wrapper.getComponent({ name: 'AddSchemaFromLedger' });
  });

  test('mount with showWritableComponents false does not have CreateSchema component', async () => {
    configStore.config.frontend.showWritableComponents = false;
    const wrapper = mountSchemas();

    expect(wrapper.findComponent({ name: 'CreateSchema' }).exists()).toBe(
      false
    );
    expect(
      wrapper.findComponent({ name: 'AddSchemaFromLedger' }).exists()
    ).toBe(false);
  });

  test('the data table is populated with expected data when there is schemas', async () => {
    const wrapper = mountSchemas();

    const elements = wrapper.findAll('tbody td').length;

    expect(elements).toBeGreaterThan(1);
    expect(
      wrapper.findComponent({ name: 'NestedCredentialDefinition' }).exists()
    ).toBe(true);
  });

  test('there is empty when there is no schemas', async () => {
    governanceStore.schemaList.value = [];
    const wrapper = mountSchemas();

    const elements = wrapper.findAll('tbody td').length;

    expect(elements).toBeLessThanOrEqual(1);
    expect(
      wrapper.findComponent({ name: 'NestedCredentialDefinition' }).exists()
    ).toBe(false);
  });
});
