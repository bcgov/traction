import { createTestingPinia } from '@pinia/testing';
import { flushPromises, mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test } from 'vitest';

import MessageConnectionList from '@/components/connections/messageConnection/MessageConnectionList.vue';
import { useMessageStore } from '@/store';

const mountMessageConnection = () =>
  mount(MessageConnectionList, {
    props: {
      connectionId: 'test-connection-id',
      connectionName: 'test-connection-name',
    },
    global: {
      plugins: [PrimeVue, createTestingPinia()],
    },
  });

describe('MessageConnection', () => {
  test('mount calls listMessage and list elements have expected classes', async () => {
    const wrapper = await mountMessageConnection();
    const store = useMessageStore();
    await flushPromises();

    expect(store.listMessages).toHaveBeenCalled();

    // This is somewhat brittle. Possibly better to use a data-testid.
    expect(wrapper.html()).toContain('class="mine message"');
    expect(wrapper.html()).toContain('class="bubble"');
    expect(wrapper.html()).toContain('class="time display"');
  });
});
