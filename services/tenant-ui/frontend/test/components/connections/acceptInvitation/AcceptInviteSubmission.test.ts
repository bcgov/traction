import { createTestingPinia } from '@pinia/testing';
import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test, vi } from 'vitest';
import VueToastificationPlugin from 'vue-toastification';

import AcceptInviteSubmission from '@/components/connections/acceptInvitation/AcceptInviteSubmission.vue';
import { useConnectionStore } from '@/store';

import { acceptInviteSubmission } from '../../../__mocks__/validation/forms';

// Mocks
vi.mock('@vuelidate/core');

const mockVuelidate = async (values: object = acceptInviteSubmission) => {
  const vuelidateMock = await import('@vuelidate/core');
  vuelidateMock.useVuelidate = vi.fn().mockReturnValue({
    ...values,
    value: {
      $touch: vi.fn(),
    },
  });
};

vi.mock('vue', async () => {
  const actual = await vi.importActual<typeof import('vue')>('vue');
  return {
    ...actual,
    reactive: vi.fn(() => ({
      did: 'test',
      alias: 'test',
    })),
  };
});

// Tests
const mountAcceptInviteSubmission = () =>
  mount(AcceptInviteSubmission, {
    props: {
      invitationString:
        'eyJAdHlwZSI6ICJodHRwczovL2RpZGNvbW0ub3JnL2Nvbm5lY3Rpb25zLzEuMC9pbnZpdGF0aW9uIiwgIkBpZCI6ICI4ZmJjMjkzNC1mN2QxLTRmNDYtYWE5OC00MTI1Mjg0N2IzYjkiLCAibGFiZWwiOiAiSmFtaWUiLCAicmVjaXBpZW50S2V5cyI6IFsiN3BaNFNNZDdLQkRTcVBUMkhVbnNib2NKMVlqWlFNcnp6Y0djc2ZONU5mVHIiXSwgInNlcnZpY2VFbmRwb2ludCI6ICJodHRwczovLzI2ODItNzAtNjYtMTQwLTEwNS5uZ3Jvay1mcmVlLmFwcCJ9',
    },
    global: {
      plugins: [PrimeVue, VueToastificationPlugin, createTestingPinia()],
    },
  });

describe('AcceptInviteSubmission', async () => {
  test('renders as snapshot', async () => {
    await mockVuelidate();

    const wrapper = mountAcceptInviteSubmission();

    wrapper.getComponent({ name: 'Textarea' });
    wrapper.getComponent({ name: 'InputText' });
    wrapper.getComponent({ name: 'Button' });
  });

  test('invitationJson field error displays when invalid', async () => {
    const values = JSON.parse(JSON.stringify(acceptInviteSubmission));
    values.alias.$invalid = true;
    values.$invalid = true;
    await mockVuelidate(values);

    const wrapper = mountAcceptInviteSubmission();

    await wrapper.find('form').trigger('submit.prevent');
    expect(wrapper.html()).toContain('Alias is required');
  });

  test('sucessful form calls toast info and external function', async () => {
    await mockVuelidate();
    const wrapper = mountAcceptInviteSubmission();
    const wrapperVm = wrapper.vm as unknown as typeof AcceptInviteSubmission;
    const toastInfoSpy = vi.spyOn(wrapperVm.toast, 'info');
    const toastErrorSpy = vi.spyOn(wrapperVm.toast, 'error');
    const store = useConnectionStore();

    await wrapper.find('form').trigger('submit.prevent');

    expect(toastErrorSpy).not.toHaveBeenCalled();
    expect(toastInfoSpy).toHaveBeenCalled();
    expect(store.receiveInvitation).toHaveBeenCalled();
  });
});
