import { createTestingPinia } from '@pinia/testing';
import { flushPromises, shallowMount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test, vi } from 'vitest';
import VueToastificationPlugin from 'vue-toastification';

import RegenerateInvitation from '@/components/connections/createConnection/RegenerateInvitation.vue';
import { useConnectionStore } from '@/store';

const mountRegenerateInvitation = () =>
  shallowMount(RegenerateInvitation, {
    props: {
      connectionId: 'test_connection_id',
    },
    global: {
      plugins: [PrimeVue, VueToastificationPlugin, createTestingPinia()],
    },
  });

describe('RegenerateInvitation', async () => {
  test('renders with expected components', async () => {
    const wrapper = mountRegenerateInvitation();

    wrapper.getComponent({ name: 'Button' });
    expect(wrapper.getComponent({ name: 'Dialog' }).attributes().visible).toBe(
      'false'
    );
  });

  test('sucessful form calls toast info and external function', async () => {
    const wrapper = mountRegenerateInvitation();
    const wrapperVm = wrapper.vm as unknown as typeof RegenerateInvitation;
    const toastErrorSpy = vi.spyOn(wrapperVm.toast, 'error');
    const store = useConnectionStore();
    wrapper.getComponent({ name: 'Button' }).trigger('click');

    await flushPromises();

    expect(toastErrorSpy).not.toHaveBeenCalled();
    expect(store.getInvitation).toHaveBeenCalled();
  });
});
