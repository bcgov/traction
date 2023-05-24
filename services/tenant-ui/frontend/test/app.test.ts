import { expect, test, vi } from 'vitest';

import App from '../src/App.vue';
import { mount } from '@vue/test-utils';

vi.mock('pinia', () => ({
  defineStore: vi.fn(),
  storeToRefs: vi.fn(() => ({
    config: {
      value: {
        frontend: {
          ux: {
            appTitle: 'Tenant UI',
          },
        },
      },
    },
  })),
}));
vi.mock('@/store/configStore', () => ({
  useConfigStore: vi.fn(),
}));

test('mount App', () => {
  const wrapper = mount(App);

  expect(App).toBeTruthy();
  expect(wrapper.html()).toMatchSnapshot();
});
