import { createTestingPinia } from '@pinia/testing';
import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test, vi } from 'vitest';

import EditConnectionForm from '@/components/connections/editConnection/EditConnectionForm.vue';
import { useConnectionStore } from '@/store';

import { basicAlias } from '../../../__mocks__/validation/forms';

// Mocks
vi.mock('@vuelidate/core');

const mockVuelidate = async (values: object = basicAlias) => {
  const vuelidateMock = await import('@vuelidate/core');
  vuelidateMock.useVuelidate = vi.fn().mockReturnValue(values);
};

const mountEditConnectionForm = () =>
  mount(EditConnectionForm, {
    props: {
      connectionId: 'test-connection-id',
    },
    global: {
      plugins: [PrimeVue, createTestingPinia()],
    },
  });

// Tests
describe('EditConnectionForm', async () => {
  test('renders with expected components', async () => {
    await mockVuelidate();

    const wrapper = mountEditConnectionForm();

    wrapper.getComponent({ name: 'InputText' });
    wrapper.getComponent({ name: 'Button' });
  });

  test('alias field error displays when invalid', async () => {
    const values = JSON.parse(JSON.stringify(basicAlias));
    values.alias.$invalid = true;
    values.$invalid = true;
    await mockVuelidate(values);

    const wrapper = mountEditConnectionForm();
    await wrapper.find('form').trigger('submit.prevent');

    expect(wrapper.html()).toContain('Alias is required');
  });

  test('sucessful form calls toast info and external function', async () => {
    await mockVuelidate();
    const wrapper = mountEditConnectionForm();
    const store = useConnectionStore();
    await wrapper.find('form').trigger('submit.prevent');

    expect(store.updateConnection).toHaveBeenCalled();
  });
});
