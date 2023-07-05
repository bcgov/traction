import { createTestingPinia } from '@pinia/testing';
import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import ConfirmationService from 'primevue/confirmationservice';
import { describe, expect, test, vi } from 'vitest';

import DeleteContact from '@/components/connections/editContact/DeleteContact.vue';

const mountDeleteContact = () =>
  mount(DeleteContact, {
    props: {
      connectionId: 'test-connection-id',
    },
    global: {
      plugins: [PrimeVue, createTestingPinia(), ConfirmationService],
    },
  });

describe('DeleteContact', () => {
  test('mount has expected components and calls delete on click', async () => {
    const wrapper = mountDeleteContact();
    const wrapperVm = wrapper.vm as unknown as typeof DeleteContact;
    const spy = vi.spyOn(wrapperVm.confirm, 'require');
    wrapper
      .getComponent({ name: 'Button', props: { icon: 'pi pi-trash' } })
      .trigger('click');
    expect(spy).toHaveBeenCalled();
  });
});
