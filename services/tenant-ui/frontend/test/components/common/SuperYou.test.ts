import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test } from 'vitest';

import SuperYou from '@/components/common/SuperYou.vue';

describe('SuperYou', () => {
  test('mount matches snapshot with expected values', async () => {
    const wrapper = mount(SuperYou, {
      props: {
        apiUrl: 'http://test.com',
        templateJson: {
          name: 'test',
        },
        icon: 'pi-user',
        text: 'test test',
      },
      global: {
        plugins: [PrimeVue],
      },
    });

    expect(wrapper.html()).toMatchSnapshot();
  });
});
