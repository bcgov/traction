import { useConfigStore } from '@/store/configStore';
import { createTestingPinia } from '@pinia/testing';
import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test } from 'vitest';

import Acapy from '@/components/about/Acapy.vue';

const createWrapper = () =>
  mount(Acapy, {
    global: {
      plugins: [PrimeVue, createTestingPinia()],
    },
  });

describe('Acapy', async () => {
  test('mount matches snapshot with expected values', () => {
    expect(createWrapper().html()).toMatchSnapshot();
  });

  test('clicking accordion calls getPluginsList', async () => {
    const store = useConfigStore();
    const wrapper = createWrapper();
    wrapper.getComponent({ name: 'Accordion' }).trigger('click');
  });
});
