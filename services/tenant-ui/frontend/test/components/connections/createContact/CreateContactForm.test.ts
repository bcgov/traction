import { createTestingPinia } from '@pinia/testing';
import { flushPromises, shallowMount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test, vi } from 'vitest';
import VueToastificationPlugin from 'vue-toastification';

import CreateConnectionForm from '@/components/connections/createConnection/CreateConnectionForm.vue';
import { useConnectionStore } from '@/store';

import { basicAlias } from '../../../__mocks__/validation/forms';

// Mocks
vi.mock('@vuelidate/core');

const mockVuelidate = async (values: object = basicAlias) => {
  const vuelidateMock = await import('@vuelidate/core');
  vuelidateMock.useVuelidate = vi.fn().mockReturnValue(values);
};

// Tests
const mountCreateConnectionForm = () =>
  shallowMount(CreateConnectionForm, {
    props: {
      multi: false,
    },
    global: {
      plugins: [PrimeVue, VueToastificationPlugin, createTestingPinia()],
    },
  });

describe('CreateConnectionForm', async () => {
  test('renders as snapshot', async () => {
    await mockVuelidate();

    const wrapper = mountCreateConnectionForm();

    wrapper.getComponent({ name: 'InputText' });
    wrapper.getComponent({ name: 'Button' });
  });

  test('did field error displays when invalid', async () => {
    const values = JSON.parse(JSON.stringify(basicAlias));
    values.alias.$invalid = true;
    values.$invalid = true;
    await mockVuelidate(values);

    const wrapper = mountCreateConnectionForm();

    await wrapper.find('form').trigger('submit.prevent');
    expect(wrapper.html()).toContain('Alias is required');
  });

  test('sucessful form calls toast info and external function', async () => {
    await mockVuelidate();
    const wrapper = mountCreateConnectionForm();
    const store = useConnectionStore();
    const wrapperVm = wrapper.vm as unknown as typeof CreateConnectionForm;
    const toastInfoSpy = vi.spyOn(wrapperVm.toast, 'info');
    const toastErrorSpy = vi.spyOn(wrapperVm.toast, 'error');

    await flushPromises();
    await wrapper.find('form').trigger('submit.prevent');

    expect(toastErrorSpy).not.toHaveBeenCalled();
    expect(toastInfoSpy).toHaveBeenCalled();
    expect(store.createInvitation).toHaveBeenCalled();
  });
});
