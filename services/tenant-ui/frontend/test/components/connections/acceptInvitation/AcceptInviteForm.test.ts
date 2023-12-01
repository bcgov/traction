import { shallowMount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test, vi } from 'vitest';
import VueToastificationPlugin from 'vue-toastification';

import AcceptInviteForm from '@/components/connections/acceptInvitation/AcceptInviteForm.vue';

import { acceptInvite } from '../../../__mocks__/validation/forms';

// Mocks
vi.mock('@vuelidate/core');

const mockVuelidate = async (values: object = acceptInvite) => {
  const vuelidateMock = await import('@vuelidate/core');
  vuelidateMock.useVuelidate = vi.fn().mockReturnValue(values);
};

vi.mock('@/helpers', () => ({
  paramFromUrlString: vi
    .fn()
    .mockReturnValue(
      'eyJAdHlwZSI6ICJodHRwczovL2RpZGNvbW0ub3JnL2Nvbm5lY3Rpb25zLzEuMC9pbnZpdGF0aW9uIiwgIkBpZCI6ICI4ZmJjMjkzNC1mN2QxLTRmNDYtYWE5OC00MTI1Mjg0N2IzYjkiLCAibGFiZWwiOiAiSmFtaWUiLCAicmVjaXBpZW50S2V5cyI6IFsiN3BaNFNNZDdLQkRTcVBUMkhVbnNib2NKMVlqWlFNcnp6Y0djc2ZONU5mVHIiXSwgInNlcnZpY2VFbmRwb2ludCI6ICJodHRwczovLzI2ODItNzAtNjYtMTQwLTEwNS5uZ3Jvay1mcmVlLmFwcCJ9'
    ),
}));

Object.defineProperty(window, 'atob', vi.fn());

// Tests
const mountAcceptInviteForm = () =>
  shallowMount(AcceptInviteForm, {
    global: {
      plugins: [PrimeVue, VueToastificationPlugin],
    },
  });

describe('AcceptInviteForm', async () => {
  test('renders as snapshot', async () => {
    await mockVuelidate();

    const wrapper = mountAcceptInviteForm();

    wrapper.getComponent({
      name: 'Button',
      props: { icon: 'pi pi-arrow-right' },
    });
    wrapper.getComponent({ name: 'InputText' });
  });

  test('did field error displays when invalid', async () => {
    const values = JSON.parse(JSON.stringify(acceptInvite));
    values.inviteUrl.$invalid = true;
    values.$invalid = true;
    await mockVuelidate(values);
    const wrapper = mountAcceptInviteForm();

    await wrapper.find('form').trigger('submit.prevent');

    expect(wrapper.html()).toContain('Url is required');
  });

  test.skip('sucessful form calls toast info and external function', async () => {
    await mockVuelidate();
    const wrapper = mountAcceptInviteForm();
    const wrapperVm = wrapper.vm as unknown as typeof AcceptInviteForm;
    const toastSpy = vi.spyOn(wrapperVm.toast, 'error');

    await wrapper.find('form').trigger('submit.prevent');

    expect(toastSpy).not.toHaveBeenCalled();
  });
});
