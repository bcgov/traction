import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test } from 'vitest';

import LoadingLabel from '@/components/common/LoadingLabel.vue';

interface Props {
  value: string | undefined;
  size: number | undefined;
}

const mountLoadingLabel = (props: Props) =>
  mount(LoadingLabel, {
    props,
    global: {
      plugins: [PrimeVue],
    },
  });

describe('LoadingLabel', () => {
  test('renders loading spinner with undefined value', async () => {
    const props = {
      value: undefined,
      size: undefined,
    };
    const wrapper = mountLoadingLabel(props);

    wrapper.getComponent({ name: 'ProgressSpinner' });
  });

  test('renders value with string value', async () => {
    const props = {
      value: 'test-value',
      size: undefined,
    };
    const wrapper = mountLoadingLabel(props);

    expect(wrapper.text()).toBe('test-value');
  });

  test('renders blank string with blank string value', async () => {
    const props = {
      value: '',
      size: undefined,
    };
    const wrapper = mountLoadingLabel(props);

    expect(wrapper.text()).toBe('');
  });

  test('changes size of spinner when setting size prop', async () => {
    const props = {
      value: undefined,
      size: 10,
    };
    const wrapper = mountLoadingLabel(props);

    expect(wrapper.html()).toContain('width: 10rem; height: 10rem;');
  });
});
