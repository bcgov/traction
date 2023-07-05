import { flushPromises, mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test, vi } from 'vitest';

import RowExpandData from '@/components/common/RowExpandData.vue';
import { defineComponent } from 'vue';

vi.mock('@/composables/useGetItem');

const useGetItemResponse = {
  loading: true,
  item: null as null | object,
  fetchItem: vi.fn(),
};

const mockUseGetItem = async () => {
  vi.mock('@/composables/useGetItem', () => ({
    default: vi.fn(() => useGetItemResponse),
  }));
};

const TestComponent = defineComponent({
  components: { RowExpandData },
  template:
    "<Suspense><RowExpandData url='http://test.com' id='123' /></Suspense>",
});

const mountRowExpandData = () =>
  mount(TestComponent, {
    global: {
      plugins: [PrimeVue],
      stubs: ['Accordion'],
    },
  });

describe('RowExpandData', () => {
  test('initially loads spinner', async () => {
    mockUseGetItem();

    const wrapper = mountRowExpandData();
    await flushPromises();

    expect(wrapper.getComponent({ name: 'ProgressSpinner' }).isVisible()).toBe(
      true
    );
  });

  test('loads accordion after loading with items', async () => {
    useGetItemResponse.loading = false;
    useGetItemResponse.item = { item: 'item' };
    mockUseGetItem();

    const wrapper = mountRowExpandData();
    await flushPromises();

    expect(wrapper.getComponent({ name: 'Accordion' }).isVisible()).toBe(true);
  });
});
