import { flushPromises, mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test } from 'vitest';

import StatusChip from '@/components/common/StatusChip.vue';

describe('StatusChip', () => {
  test('mount matches snapshot with expected values', async () => {
    const wrapper = mount(StatusChip, {
      props: {
        status: 'kebabTest',
        class: 'test-class',
      },
      global: {
        plugins: [PrimeVue],
      },
    });

    await flushPromises();

    const expectedClasses = [
      'test-class',
      'kebab-test',
      'status-chip',
      'p-chip',
    ];

    // Tests that all expected classes are present in component
    expect(expectedClasses.every((c) => wrapper.classes().includes(c))).toBe(
      true
    );
  });
});
