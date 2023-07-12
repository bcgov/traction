import { createTestingPinia } from '@pinia/testing';
import { flushPromises, mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import ConfirmationService from 'primevue/confirmationservice';
import { describe, expect, test, vi } from 'vitest';

import Connections from '@/components/connections/Connections.vue';
import { useTenantStore } from '@/store';

import { tenantStore } from '../../__mocks__/store';

const mountConnections = () =>
  mount(Connections, {
    global: {
      plugins: [PrimeVue, createTestingPinia(), ConfirmationService],
    },
  });

describe('Connections', () => {
  test('mount renders with expected components', async () => {
    const wrapper = mountConnections();

    wrapper.getComponent({ name: 'MainCardContent' });
    wrapper.getComponent({ name: 'DataTable' });
    wrapper.getComponent({ name: 'AcceptInvitation' });
    wrapper.getComponent({ name: 'DidExchange' });
  });

  test('onMounted triggers getEndorserInfo', async () => {
    mountConnections();
    const store = useTenantStore();

    expect(store.getEndorserInfo).toHaveBeenCalled();
  });

  test.todo('formattedConnections maps connections and they render correctly');

  test('deleteDisabled return truthy when endorser name is input parameter', async () => {
    tenantStore.endorserInfo.value = {
      endorser_name: 'test.alias',
    };
    const wrapper = mountConnections();

    expect(
      wrapper.findAll('tbody td button')[2].attributes('disabled')
    ).not.toBeUndefined();
  });

  test('deleteDisabled return falsy when endorser name is not input paramter', async () => {
    tenantStore.endorserInfo.value = {
      endorser_name: null,
    };
    const wrapper = mountConnections();

    expect(
      wrapper.findAll('tbody td button')[2].attributes('disabled')
    ).toBeFalsy();
  });

  test('clicking delete button triggers delete contact function and confirmation dialog', async () => {
    tenantStore.endorserInfo.value = {
      endorser_name: null,
    };
    const wrapper = mountConnections();
    const wrapperVm = wrapper.vm as unknown as typeof Connections;
    const spy = vi.spyOn(wrapperVm.confirm, 'require');

    await wrapper.findAll('tbody td button')[2].trigger('click');

    expect(spy).toHaveBeenCalled();
  });
});
