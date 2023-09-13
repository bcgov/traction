import { createTestingPinia } from '@pinia/testing';
import { flushPromises, mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test, vi } from 'vitest';

import InnkeeperLoginForm from '@/components/innkeeper/InnkeeperLoginForm.vue';
import { useInnkeeperTokenStore } from '@/store';

import { innkeeperLogin } from '../../__mocks__/validation/forms';
import { beforeEach } from 'node:test';

// Mocks
vi.mock('@vuelidate/core');

vi.mock('vue-router');

const mockRouter = async (name = 'test') => {
  const routerMock = await import('vue-router');
  routerMock.useRoute = vi.fn().mockReturnValue({
    name,
  });
  routerMock.useRouter = vi.fn().mockReturnValue({
    push: vi.fn(),
  });
};

const mockVuelidate = async (values: object = innkeeperLogin) => {
  const vuelidateMock = await import('@vuelidate/core');
  vuelidateMock.useVuelidate = vi.fn().mockReturnValue(values);
};

// Tests
const mountLoginForm = () =>
  mount(InnkeeperLoginForm, {
    global: {
      plugins: [PrimeVue, createTestingPinia()],
    },
  });

describe('InnkeeperLoginForm', async () => {
  test('renders with expected inner components', async () => {
    await mockRouter();
    await mockVuelidate();
    const wrapper = mountLoginForm();

    expect(wrapper.findAllComponents({ name: 'InputText' })).toHaveLength(2);
    wrapper.getComponent({ name: 'Button' });
  });

  test('invalid admin name renders error message', async () => {
    await mockRouter();
    const loginValues = JSON.parse(JSON.stringify(innkeeperLogin));
    loginValues.adminName.$invalid = true;
    loginValues.$invalid = true;
    await mockVuelidate(loginValues);
    const wrapper = mountLoginForm();
    await wrapper.find('form').trigger('submit.prevent');
    expect(wrapper.html()).toContain('Name is required');
  });

  test('invalid admin key renders error message', async () => {
    await mockRouter();
    const loginValues = JSON.parse(JSON.stringify(innkeeperLogin));
    loginValues.adminKey.$invalid = true;
    loginValues.$invalid = true;
    await mockVuelidate(loginValues);
    const wrapper = mountLoginForm();
    await wrapper.find('form').trigger('submit.prevent');
    expect(wrapper.html()).toContain('Key is required');
  });

  test('successful login triggers expected methods', async () => {
    await mockRouter();
    await mockVuelidate();
    const wrapper = mountLoginForm();
    const wrapperVm = wrapper.vm as unknown as typeof InnkeeperLoginForm;
    const toastSpy = vi.spyOn(wrapperVm.toast, 'error');
    const tokenStore = useInnkeeperTokenStore();

    await wrapper.find('form').trigger('submit.prevent');

    expect(tokenStore.login).toHaveBeenCalled();
    expect(toastSpy).not.toHaveBeenCalled();
  });

  test('if login call fails, toast error triggered in catch block', async () => {
    await mockRouter();
    const wrapper = mountLoginForm();
    const wrapperVm = wrapper.vm as unknown as typeof InnkeeperLoginForm;
    const toastSpy = vi.spyOn(wrapperVm.toast, 'error');
    const tokenStore = useInnkeeperTokenStore();
    tokenStore.login = vi.fn().mockRejectedValue('fail');

    await wrapper.find('form').trigger('submit.prevent');
    await flushPromises();

    expect(toastSpy).toHaveBeenCalled();
  });
});
