import { createTestingPinia } from '@pinia/testing';
import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test, vi } from 'vitest';

import InnkeeperLoginOidc from '@/components/innkeeper/InnkeeperLoginOidc.vue';
import { useInnkeeperOidcStore } from '@/store';

const mountLoginOidc = () =>
  mount(InnkeeperLoginOidc, {
    global: {
      plugins: [PrimeVue, createTestingPinia()],
    },
  });

describe('InnkeeperLoginOidc', async () => {
  test('renders with expected components', async () => {
    const wrapper = mountLoginOidc();

    expect(wrapper.findComponent({ name: 'InputText' }).exists()).toBeFalsy();
    wrapper.getComponent({ name: 'Button' });
  });

  test('button click triggers login', async () => {
    const wrapper = mountLoginOidc();
    const store = useInnkeeperOidcStore();
    await wrapper.getComponent({ name: 'Button' }).trigger('click');

    expect(store.login).toHaveBeenCalled();
  });

  test('failed login displays toast error', async () => {
    const wrapper = mountLoginOidc();
    const wrapperVm = wrapper.vm as unknown as typeof InnkeeperLoginOidc;
    const toastSpy = vi.spyOn(wrapperVm.toast, 'error');
    const store = useInnkeeperOidcStore();
    store.login = vi.fn().mockRejectedValue('fail');
    await wrapper.getComponent({ name: 'Button' }).trigger('click');

    expect(toastSpy).toHaveBeenCalled();
  });
});
