import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test, vi } from 'vitest';
import { createTestingPinia } from '@pinia/testing';
import VueToastificationPlugin from 'vue-toastification';

import DidExchangeForm from '@/components/connections/didExchange/DidExchangeForm.vue';
import { useConnectionStore } from '@/store';

import { connectionStore, tenantStore } from '../../../__mocks__/store';
import { didCreateRequest } from '../../../__mocks__/validation/forms';

// Mocks
vi.mock('@vuelidate/core');

const mockVuelidate = async (values: object = didCreateRequest) => {
  const vuelidateMock = await import('@vuelidate/core');
  vuelidateMock.useVuelidate = vi.fn().mockReturnValue(values);
};

// Tests
const mountDidExchangeForm = () =>
  mount(DidExchangeForm, {
    global: {
      plugins: [
        PrimeVue,
        VueToastificationPlugin,
        createTestingPinia({
          initialState: Object.assign(connectionStore, tenantStore),
        }),
      ],
    },
  });

describe('DidExchangeForm', async () => {
  test('renders with expected components', async () => {
    await mockVuelidate();

    const wrapper = mountDidExchangeForm();

    expect(wrapper.findAllComponents({ name: 'InputText' })).toHaveLength(2);
    wrapper.getComponent({ name: 'Button' });
  });

  test('did field error displays when invalid', async () => {
    const values = JSON.parse(JSON.stringify(didCreateRequest));
    values.did.$invalid = true;
    values.$invalid = true;
    await mockVuelidate(values);

    const wrapper = mountDidExchangeForm();

    await wrapper.find('form').trigger('submit.prevent');
    expect(wrapper.html()).toContain('DID is required');
  });

  test('alias field error displays when invalid', async () => {
    const values = JSON.parse(JSON.stringify(didCreateRequest));
    values.alias.$invalid = true;
    values.$invalid = true;
    await mockVuelidate(values);

    const wrapper = mountDidExchangeForm();
    await wrapper.find('form').trigger('submit.prevent');

    expect(wrapper.html()).toContain('Alias is required');
  });

  test('sucessful form calls toast info and external function', async () => {
    await mockVuelidate();
    const wrapper = mountDidExchangeForm();
    const wrapperVm = wrapper.vm as unknown as typeof DidExchangeForm;
    const toastInfoSpy = vi.spyOn(wrapperVm.toast, 'info');
    const toastErrorSpy = vi.spyOn(wrapperVm.toast, 'error');
    const store = useConnectionStore();

    await wrapper.find('form').trigger('submit.prevent');

    expect(toastErrorSpy).not.toHaveBeenCalled();
    expect(toastInfoSpy).toHaveBeenCalled();
    expect(store.didCreateRequest).toHaveBeenCalled();
  });
});
