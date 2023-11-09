import { createTestingPinia } from '@pinia/testing';
import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test, vi } from 'vitest';

import SessionTimeoutModal from '@/components/common/SessionTimeoutModal.vue';

const mountSessionTimeoutModal = () =>
  mount(SessionTimeoutModal, {
    global: {
      plugins: [PrimeVue, createTestingPinia()],
      stubs: ['Dialog'],
    },
  });

describe('SessionTimeoutModal', () => {
  test('modal is hippen on initial mount', async () => {
    const wrapper = mountSessionTimeoutModal();

    expect(wrapper.getComponent({ name: 'Dialog' }).attributes().visible).toBe(
      'false'
    );
  });
});
