import { createTestingPinia } from '@pinia/testing';
import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import ConfirmationService from 'primevue/confirmationservice';
import { describe, expect, test, vi } from 'vitest';

import DeleteConnection from '@/components/connections/editConnection/DeleteConnection.vue';

const mountDeleteConnection = () =>
  mount(DeleteConnection, {
    props: {
      connectionId: 'test-connection-id',
    },
    global: {
      plugins: [PrimeVue, createTestingPinia(), ConfirmationService],
    },
  });

describe('DeleteConnection', () => {
  test('mount has expected components and calls delete on click', async () => {
    const wrapper = mountDeleteConnection();
    const wrapperVm = wrapper.vm as unknown as typeof DeleteConnection;
    const spy = vi.spyOn(wrapperVm.confirm, 'require');
    wrapper
      .getComponent({ name: 'Button', props: { icon: 'pi pi-trash' } })
      .trigger('click');
    expect(spy).toHaveBeenCalled();
  });
});
