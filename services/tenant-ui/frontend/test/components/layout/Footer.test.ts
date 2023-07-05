import { mount } from '@vue/test-utils';
import { describe, expect, test } from 'vitest';

import Footer from '@/components/layout/Footer.vue';

describe('Header', async () => {
  test('mount matches snapshot with expected values', () => {
    const wrapper = mount(Footer);

    expect(wrapper.html()).toMatchSnapshot();
  });
});
