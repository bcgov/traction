import { createTestingPinia } from '@pinia/testing';
import { flushPromises, shallowMount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test, vi } from 'vitest';
import VueToastificationPlugin from 'vue-toastification';

import CreateContactForm from '@/components/connections/createContact/CreateContactForm.vue';
import { useContactsStore } from '@/store';

import { basicAlias } from '../../../__mocks__/validation/forms';

// Mocks
vi.mock('@vuelidate/core');

const mockVuelidate = async (values: object = basicAlias) => {
  const vuelidateMock = await import('@vuelidate/core');
  vuelidateMock.useVuelidate = vi.fn().mockReturnValue(values);
};

// Tests
const mountCreateContactForm = () =>
  shallowMount(CreateContactForm, {
    props: {
      multi: false,
    },
    global: {
      plugins: [PrimeVue, VueToastificationPlugin, createTestingPinia()],
    },
  });

describe('CreateContactForm', async () => {
  test('renders as snapshot', async () => {
    await mockVuelidate();

    const wrapper = mountCreateContactForm();

    wrapper.getComponent({ name: 'InputText' });
    wrapper.getComponent({ name: 'Button' });
  });

  test('did field error displays when invalid', async () => {
    const values = JSON.parse(JSON.stringify(basicAlias));
    values.alias.$invalid = true;
    values.$invalid = true;
    await mockVuelidate(values);

    const wrapper = mountCreateContactForm();

    await wrapper.find('form').trigger('submit.prevent');
    expect(wrapper.html()).toContain('Alias is required');
  });

  test('sucessful form calls toast info and external function', async () => {
    await mockVuelidate();
    const wrapper = mountCreateContactForm();
    const store = useContactsStore();
    const wrapperVm = wrapper.vm as unknown as typeof CreateContactForm;
    const toastInfoSpy = vi.spyOn(wrapperVm.toast, 'info');
    const toastErrorSpy = vi.spyOn(wrapperVm.toast, 'error');

    await flushPromises();
    await wrapper.find('form').trigger('submit.prevent');

    expect(toastErrorSpy).not.toHaveBeenCalled();
    expect(toastInfoSpy).toHaveBeenCalled();
    expect(store.createInvitation).toHaveBeenCalled();
  });
});
