import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test } from 'vitest';

import LocaleSwitcher from '@/components/common/LocaleSwitcher.vue';

const mountLocaleSwitcher = () =>
  mount(LocaleSwitcher, {
    global: {
      plugins: [PrimeVue],
    },
  });

describe('LocaleSwitcher', () => {
  test('mount matches snapshot with expected values', async () => {
    const wrapper = mountLocaleSwitcher();

    expect(wrapper.html()).toMatchSnapshot();
  });
});
