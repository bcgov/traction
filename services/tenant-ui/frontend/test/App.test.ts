import { mount } from '@vue/test-utils';
import { describe, expect, test } from 'vitest';

import App from '@/App.vue';

describe('App Component', async () => {
  const wrapper = mount(App, {
    global: {
      stubs: ['router-view'],
    },
  });

  test('renders as snapshot', () => {
    expect(App).toBeTruthy();
    expect(wrapper.html()).toMatchSnapshot();
  });
});
