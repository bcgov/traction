import { createTestingPinia } from '@pinia/testing';
import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test, vi } from 'vitest';

import SessionTimeoutModal from '@/components/common/SessionTimeoutModal.vue';

vi.mock('global.localStorage', () => ({
  getItem: vi.fn().mockReturnValue('true'),
}));

const getLocalStorageSpy = vi.spyOn(Storage.prototype, 'getItem');

const mountSessionTimeoutModal = () =>
  mount(SessionTimeoutModal, {
    global: {
      plugins: [PrimeVue, createTestingPinia()],
      stubs: ['Dialog'],
    },
  });

describe('SessionTimeoutModal', () => {
  test('mounting checks local storage', async () => {
    mountSessionTimeoutModal();

    expect(getLocalStorageSpy).toHaveBeenCalledTimes(1);
  });

  test('modal is hippen on initial mount', async () => {
    const wrapper = mountSessionTimeoutModal();

    expect(wrapper.getComponent({ name: 'Dialog' }).attributes().visible).toBe(
      'false'
    );
  });
});
