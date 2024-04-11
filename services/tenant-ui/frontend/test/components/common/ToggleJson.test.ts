import CreateSchema from '@/components/issuance/schemas/CreateSchema.vue';
import { shallowMount, mount, flushPromises } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test, vi } from 'vitest';
import VueToastificationPlugin from 'vue-toastification';
import { tryParseJson } from '@/helpers/jsonParsing';

import ToggleJson from '@/components/common/ToggleJson.vue';

const mountToggleJson = () =>
  shallowMount(ToggleJson, {
    props: {
      toJson: () => {
        return "{ 'testing': 1 }";
      },
      fromJson: (jsonRepresentation: string) => {
        return tryParseJson<any>(jsonRepresentation);
      },
    },
    slots: {
      default: [CreateSchema, '<my-component />', 'text'],
    },
    global: {
      plugins: [PrimeVue, VueToastificationPlugin],
    },
  });

describe('Properly Toggle Json Input', () => {
  test('reders properly', async () => {
    const wrapper = mountToggleJson();

    expect(wrapper.exists()).toBe(true);
  });
  test('text area is only shown after input is toggled', async () => {
    const wrapper = mountToggleJson();
    const wrapperVm = wrapper.vm as any;
    const toJson = vi.spyOn(wrapperVm.props, 'toJson');
    const fromJson = vi.spyOn(wrapperVm.props, 'fromJson');

    expect(wrapper.findComponent({ name: 'Textarea' }).isVisible()).toBe(false);
    // displayAsForm;
    expect(wrapper.findComponent({ name: 'InputSwitch' }).exists()).toBe(true);

    expect(wrapper.findComponent({ name: 'CreateSchema' }).exists()).toBe(true);
    wrapperVm.displayAsForm = true;
    // wrapperVm.displayAsForm = false;
    await wrapperVm.toggleJson();

    await flushPromises();

    wrapperVm.displayAsForm = false;

    await flushPromises();

    expect(toJson).toHaveBeenCalled();
    // expect(fromJson).toHaveBeenCalled();
    expect(wrapper.findComponent({ name: 'Textarea' }).isVisible()).toBe(true);

    await wrapperVm.toggleJson();

    await flushPromises();

    expect(fromJson).toHaveBeenCalled();
  });
});
