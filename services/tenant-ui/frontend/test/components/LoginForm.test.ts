import { createTestingPinia } from '@pinia/testing';
import { flushPromises, mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test, vi } from 'vitest';

import LoginForm from '@/components/LoginForm.vue';
import { useTenantStore, useTokenStore } from '@/store';

import { login } from '../__mocks__/validation/forms';
import { tokenStore } from '../__mocks__/store';

// Mocks
vi.mock('@vuelidate/core');

const mockVuelidate = async (values: object = login) => {
  const vuelidateMock = await import('@vuelidate/core');
  vuelidateMock.useVuelidate = vi.fn().mockReturnValue(values);
};

// Tests
const mountLoginForm = () =>
  mount(LoginForm, {
    global: {
      plugins: [PrimeVue, createTestingPinia()],
    },
  });

describe('LoginForm', async () => {
  test('renders with expected inner components', async () => {
    await mockVuelidate();
    const wrapper = mountLoginForm();

    expect(wrapper.findAllComponents({ name: 'InputText' })).toHaveLength(4);
    wrapper.getComponent({ name: 'Button' });
  });

  test('invalid walletId renders error message', async () => {
    const loginValues = JSON.parse(JSON.stringify(login));
    loginValues.activeTab = 0;
    loginValues.walletId.$invalid = true;
    loginValues.$invalid = true;
    await mockVuelidate(loginValues);
    const wrapper = mountLoginForm();
    await wrapper.find('form').trigger('submit.prevent');
    expect(wrapper.html()).toContain('Wallet ID is required');
  });

  test('invalid walletSecret renders error message', async () => {
    const loginValues = JSON.parse(JSON.stringify(login));
    loginValues.walletSecret.$invalid = true;
    loginValues.$invalid = true;
    await mockVuelidate(loginValues);
    const wrapper = mountLoginForm();
    await wrapper.find('form').trigger('submit.prevent');
    expect(wrapper.html()).toContain('Wallet Secret is required');
  });

  test('successful login triggers expected methods', async () => {
    await mockVuelidate();
    const wrapper = mountLoginForm();
    const wrapperVm = wrapper.vm as unknown as typeof LoginForm;
    const toastSpy = vi.spyOn(wrapperVm.toast, 'error');
    const tenantStore = useTenantStore();
    const tokenStore = useTokenStore();

    await wrapper.find('form').trigger('submit.prevent');

    expect(tokenStore.login).toHaveBeenCalled();
    expect(tenantStore.getSelf).toHaveBeenCalled();
    expect(tenantStore.getTenantConfig).toHaveBeenCalled();
    expect(tenantStore.getIssuanceStatus).toHaveBeenCalled();
    // expect(toastSpy).not.toHaveBeenCalled();
  });

  test('if login call fails, toast error triggered in catch block', async () => {
    const wrapper = mountLoginForm();
    const wrapperVm = wrapper.vm as unknown as typeof LoginForm;
    const toastSpy = vi.spyOn(wrapperVm.toast, 'error');
    const tokenStore = useTokenStore();
    tokenStore.login = vi.fn().mockRejectedValue('fail');

    await wrapper.find('form').trigger('submit.prevent');
    await flushPromises();

    expect(toastSpy).toHaveBeenCalled();
  });

  test('if getSelf call fails, toast error triggered in catch block', async () => {
    const wrapper = mountLoginForm();
    const wrapperVm = wrapper.vm as unknown as typeof LoginForm;
    const toastSpy = vi.spyOn(wrapperVm.toast, 'error');
    const tenantStore = useTenantStore();
    tenantStore.getSelf = vi.fn().mockRejectedValue('fail');
    tenantStore.getTenantConfig = vi.fn().mockResolvedValue('success');
    tenantStore.getIssuanceStatus = vi.fn().mockResolvedValue('success');

    await wrapper.find('form').trigger('submit.prevent');
    await flushPromises();

    expect(toastSpy).toHaveBeenCalled();
  });

  test('if getTenantConfig call fails, toast error triggered in catch block', async () => {
    const wrapper = mountLoginForm();
    const wrapperVm = wrapper.vm as unknown as typeof LoginForm;
    const toastSpy = vi.spyOn(wrapperVm.toast, 'error');
    const tenantStore = useTenantStore();
    tenantStore.getSelf = vi.fn().mockResolvedValue('success');
    tenantStore.getTenantConfig = vi.fn().mockRejectedValue('fail');
    tenantStore.getIssuanceStatus = vi.fn().mockResolvedValue('success');

    await wrapper.find('form').trigger('submit.prevent');
    await flushPromises();

    expect(toastSpy).toHaveBeenCalled();
  });

  test('if getIssuanceStatus call fails, toast error triggered in catch block', async () => {
    const wrapper = mountLoginForm();
    const wrapperVm = wrapper.vm as unknown as typeof LoginForm;
    const toastSpy = vi.spyOn(wrapperVm.toast, 'error');
    const tenantStore = useTenantStore();
    tenantStore.getSelf = vi.fn().mockResolvedValue('success');
    tenantStore.getTenantConfig = vi.fn().mockResolvedValue('success');
    tenantStore.getIssuanceStatus = vi.fn().mockRejectedValue('fail');

    await wrapper.find('form').trigger('submit.prevent');
    await flushPromises();

    expect(toastSpy).toHaveBeenCalled();
  });

  test('login with 404 does not call toast error and sets invalidCreds', async () => {
    const wrapper = mountLoginForm();
    const wrapperVm = wrapper.vm as unknown as typeof LoginForm;
    const toastSpy = vi.spyOn(wrapperVm.toast, 'error');
    tokenStore.token.value = null;
    const store = useTokenStore();
    store.login = vi.fn().mockRejectedValue({ response: { status: 404 } });

    await wrapper.find('form').trigger('submit.prevent');
    await flushPromises();

    expect(wrapperVm.invalidCreds).toBe(true);
    expect(toastSpy).not.toHaveBeenCalled();
  });

  test('login with 409 does not call toast error and sets invalidCreds', async () => {
    const wrapper = mountLoginForm();
    const wrapperVm = wrapper.vm as unknown as typeof LoginForm;
    const toastSpy = vi.spyOn(wrapperVm.toast, 'error');
    tokenStore.token.value = null;
    const store = useTokenStore();
    store.login = vi.fn().mockRejectedValue({ response: { status: 409 } });

    await wrapper.find('form').trigger('submit.prevent');
    await flushPromises();

    expect(wrapperVm.invalidCreds).toBe(true);
    expect(toastSpy).not.toHaveBeenCalled();
  });
});
