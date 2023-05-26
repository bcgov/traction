import { mount } from '@vue/test-utils';
import { test, expect, vi } from 'vitest';

import Traction from '../src/components/about/Traction.vue';

test('mount Traction', () => {
  const $t = vi.fn((key: string) => key);
  vi.mock('pinia', () => ({
    defineStore: vi.fn(),
    storeToRefs: vi.fn((_: any) => ({
      config: {
        frontend: {
          tenantProxyPath: '/api',
        },
        image: {
          tag: '1.0',
          version: '1.0',
          buildtime: '2021-01-01',
        },
        value: {
          frontend: {
            tenantProxyPath: '',
          },
        },
      },
    })),
  }));
  vi.mock('@/store/configStore', () => ({
    useConfigStore: vi.fn(),
  }));

  const wrapper = mount(Traction, {
    global: {
      mocks: {
        $t,
      },
    },
  });

  expect(Traction).toBeTruthy();
  expect(wrapper).toBeTruthy();
  expect($t).toHaveBeenCalled();
  expect(wrapper.html()).toContain('/api');
  expect(wrapper.html()).toContain('/api/doc');
  expect(wrapper.html()).toContain('1.0');
  expect(wrapper.html()).toContain('2021-01-01');
  expect(wrapper.html()).toMatchSnapshot();
});
