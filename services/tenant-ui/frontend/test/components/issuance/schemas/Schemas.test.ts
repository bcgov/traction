import { createTestingPinia } from '@pinia/testing';
import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import ConfirmationService from 'primevue/confirmationservice';
import { describe, expect, test } from 'vitest';

import Schemas from '@/components/issuance/schemas/Schemas.vue';

import { configStore } from '../../../__mocks__/store';

const mountSchemas = () =>
  mount(Schemas, {
    global: {
      plugins: [PrimeVue, createTestingPinia(), ConfirmationService],
    },
  });

describe('Schemas', () => {
  test('mount has expected components', async () => {
    const wrapper = mountSchemas();

    wrapper.getComponent({ name: 'CreateSchema' });
  });

  test('mount with showWritableComponents false does not have OfferCredential component', async () => {
    configStore.config.frontend.showWritableComponents = false;
    const wrapper = mountSchemas();

    expect(wrapper.findComponent({ name: 'CreateSchema' }).exists()).toBe(
      false
    );
  });
});
