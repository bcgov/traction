import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test } from 'vitest';

import SkeletonCard from '@/components/common/SkeletonCard.vue';

describe('SkeletonCard', () => {
  test('mount matches snapshot with expected values', async () => {
    const wrapper = mount(SkeletonCard, {
      global: {
        plugins: [PrimeVue],
      },
    });
    expect(wrapper.html()).toMatchSnapshot();
  });
});
