import { createTestingPinia } from '@pinia/testing';
import { flushPromises, mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test } from 'vitest';

import MessageContactList from '@/components/connections/messageContact/MessageContactList.vue';
import { useMessageStore } from '@/store';

const mountMessageContact = () =>
  mount(MessageContactList, {
    props: {
      connectionId: 'test-connection-id',
      connectionName: 'test-connection-name',
    },
    global: {
      plugins: [PrimeVue, createTestingPinia()],
    },
  });

describe('MessageContact', () => {
  test('mount calls listMessage and list elements have expected classes', async () => {
    const wrapper = await mountMessageContact();
    const store = useMessageStore();
    await flushPromises();

    expect(store.listMessages).toHaveBeenCalled();

    // This is somewhat brittle. Possibly better to use a data-testid.
    expect(wrapper.html()).toContain('class="mine message"');
    expect(wrapper.html()).toContain('class="bubble"');
    expect(wrapper.html()).toContain('class="time display"');
  });
});
