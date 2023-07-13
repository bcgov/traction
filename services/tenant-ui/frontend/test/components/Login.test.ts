import { createTestingPinia } from '@pinia/testing';
import { flushPromises, shallowMount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import ConfirmationService from 'primevue/confirmationservice';
import { describe, expect, test, vi } from 'vitest';

import Login from '@/components/Login.vue';

import { reservationStore, configStore } from '../__mocks__/store';

// Mocks
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

// Tests
const mountLogin = () =>
  shallowMount(Login, {
    global: {
      plugins: [PrimeVue, createTestingPinia(), ConfirmationService],
    },
  });

describe('LoginForm', async () => {
  test('renders with inner login form and images', async () => {
    await mockRouter();
    const wrapper = mountLogin();
    wrapper.getComponent({ name: 'LoginForm' });

    //Images from path
    expect(wrapper.html()).toContain('src="/img/bc/bc_logo.png"');
    expect(wrapper.html()).toContain(
      'src="/img/logo/traction-logo-bc-text.svg"'
    );
  });

  test('when login mode is preset to STATUS render status component', async () => {
    await mockRouter('TenantUiReservationStatus');
    const wrapper = mountLogin();
    wrapper.getComponent({ name: 'Status' });
  });

  test('when check status is clicked Status component is rendered', async () => {
    await mockRouter();
    const wrapper = mountLogin();
    await wrapper.findAll('a')[1].trigger('click');

    wrapper.getComponent({ name: 'Status' });
  });

  test('when create request is clicked Reserve component is rendered', async () => {
    await mockRouter();
    const wrapper = mountLogin();
    await wrapper.find('a').trigger('click');

    wrapper.getComponent({ name: 'Reserve' });
  });

  test('goBack() when not showing wallet renders login form', async () => {
    await mockRouter();
    const wrapper = mountLogin();
    await wrapper.find('a').trigger('click');
    await wrapper.getComponent({ name: 'Button' }).trigger('click');

    wrapper.getComponent({ name: 'LoginForm' });
  });

  test('goBack() with show wallet triggers confirm popup', async () => {
    reservationStore.status.value = 'show_wallet';
    await mockRouter();
    const wrapper = mountLogin();
    const wrapperVm = wrapper.vm as unknown as typeof Login;
    const requireSpy = vi.spyOn(wrapperVm.confirm, 'require');

    await wrapper.find('a').trigger('click');
    await wrapper.getComponent({ name: 'Button' }).trigger('click');

    expect(requireSpy).toHaveBeenCalled();
  });

  test('LoginOIDC component is rendered when user is null and oidc config true', async () => {
    configStore.config.frontend.showOIDCReservationLogin = true;
    const wrapper = mountLogin();
    await flushPromises();

    wrapper.getComponent({ name: 'LoginOIDC' });
  });
});
