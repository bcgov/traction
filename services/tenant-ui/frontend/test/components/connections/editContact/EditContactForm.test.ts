import { createTestingPinia } from '@pinia/testing';
import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test, vi } from 'vitest';

import EditContactForm from '@/components/connections/editContact/EditContactForm.vue';
import { useContactsStore } from '@/store';

import { basicAlias } from '../../../__mocks__/validation/forms';

// Mocks
vi.mock('@vuelidate/core');

const mockVuelidate = async (values: object = basicAlias) => {
  const vuelidateMock = await import('@vuelidate/core');
  vuelidateMock.useVuelidate = vi.fn().mockReturnValue(values);
};

const mountEditContactForm = () =>
  mount(EditContactForm, {
    props: {
      connectionId: 'test-connection-id',
    },
    global: {
      plugins: [PrimeVue, createTestingPinia()],
    },
  });

// Tests
describe('EditContactForm', async () => {
  test('renders with expected components', async () => {
    await mockVuelidate();

    const wrapper = mountEditContactForm();

    wrapper.getComponent({ name: 'InputText' });
    wrapper.getComponent({ name: 'Button' });
  });

  test('alias field error displays when invalid', async () => {
    const values = JSON.parse(JSON.stringify(basicAlias));
    values.alias.$invalid = true;
    values.$invalid = true;
    await mockVuelidate(values);

    const wrapper = mountEditContactForm();
    await wrapper.find('form').trigger('submit.prevent');

    expect(wrapper.html()).toContain('Alias is required');
  });

  test('sucessful form calls toast info and external function', async () => {
    await mockVuelidate();
    const wrapper = mountEditContactForm();
    const store = useContactsStore();
    await wrapper.find('form').trigger('submit.prevent');

    expect(store.updateConnection).toHaveBeenCalled();
  });
});
