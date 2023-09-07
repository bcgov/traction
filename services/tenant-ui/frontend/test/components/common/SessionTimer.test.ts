import { createTestingPinia } from '@pinia/testing';
import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test, vi } from 'vitest';

import SessionTimer from '@/components/common/SessionTimer.vue';

const mountSessionTimer = () =>
  mount(SessionTimer, {
    global: {
      plugins: [PrimeVue, createTestingPinia()],
      stubs: ['Dialog', 'router-location'],
    },
  });

describe('SessionTimer', () => {
  test('mounting creates the event listeners', async () => {
    const spy = vi.spyOn(window, 'addEventListener');
    mountSessionTimer();

    expect(spy).toHaveBeenCalledTimes(4);
  });

  test('unmounting clears the intervals', async () => {
    const spy = vi.spyOn(global, 'clearInterval');
    const wrapper = mountSessionTimer();
    await wrapper.unmount();

    expect(spy).toHaveBeenCalledTimes(2);
  });

  test('modal is hidden when countdown is false', async () => {
    const wrapper = mountSessionTimer();

    expect(wrapper.getComponent({ name: 'Dialog' }).attributes().visible).toBe(
      'false'
    );
  });

  test.todo('test the interval functionality');
});
