import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test, vi } from 'vitest';
import { createTestingPinia } from '@pinia/testing';

import CreateMessageForm from '@/components/messages/createMessage/CreateMessageForm.vue';

import { store as messagesStore } from '../../../__mocks__/store/message';
import { createMessage } from '../../../__mocks__/validation/forms';

// Mocks
vi.mock('@vuelidate/core');

const mockVuelidate = async (values: object = createMessage) => {
  const vuelidateMock = await import('@vuelidate/core');
  vuelidateMock.useVuelidate = vi.fn().mockReturnValue(values);
};

vi.mock('vue', async () => {
  const actual = await vi.importActual<typeof import('vue')>('vue');
  return {
    ...actual,
    reactive: vi.fn(() => ({
      msgContent: 'test',
      selectedConnection: {
        value: 'test',
      },
    })),
  };
});

const mountCreateMessageForm = () =>
  mount(CreateMessageForm, {
    global: {
      plugins: [PrimeVue, createTestingPinia()],
    },
  });

// Tests
describe('CreateMessageForm', async () => {
  test('renders as snapshot', async () => {
    await mockVuelidate();
    const wrapper = mountCreateMessageForm();

    wrapper.getComponent({ name: 'AutoComplete' });
    wrapper.getComponent({ name: 'Textarea' });
    expect(wrapper.findAllComponents({ name: 'Button' })).toHaveLength(2);
  });

  test('invalid msgContent renders error message', async () => {
    const values = JSON.parse(JSON.stringify(createMessage));
    values.msgContent.$invalid = true;
    values.$invalid = true;
    await mockVuelidate(values);
    const wrapper = mountCreateMessageForm();

    await wrapper.find('form').trigger('submit.prevent');

    expect(wrapper.html()).toContain('Message content is required');
  });

  test('invalid selectedConnection renders error message', async () => {
    const values = JSON.parse(JSON.stringify(createMessage));
    values.selectedConnection.$invalid = true;
    values.$invalid = true;
    await mockVuelidate(values);
    const wrapper = mountCreateMessageForm();

    await wrapper.find('form').trigger('submit.prevent');

    expect(wrapper.html()).toContain('Value is required');
  });

  test('sucessful form calls external sendMessage function', async () => {
    await mockVuelidate();
    const wrapper = mountCreateMessageForm();
    const wrapperVm = wrapper.vm as unknown as typeof CreateMessageForm;
    const toastInfoSpy = vi.spyOn(wrapperVm.toast, 'info');
    const toastErrorSpy = vi.spyOn(wrapperVm.toast, 'error');

    await wrapper.find('form').trigger('submit.prevent');

    expect(toastErrorSpy).not.toHaveBeenCalled();
    expect(toastInfoSpy).toHaveBeenCalled();
    expect(messagesStore.sendMessage).toHaveBeenCalled();
  });
});
