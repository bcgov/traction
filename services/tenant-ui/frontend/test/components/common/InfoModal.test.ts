import { flushPromises, mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test } from 'vitest';

import InfoModal from '@/components/common/InfoModal.vue';

const mountInfoModal = () =>
  mount(InfoModal, {
    props: {
      header: 'header',
      object: {
        name: 'name',
        test: 'test',
      },
    },
    global: {
      plugins: [PrimeVue],
      stubs: ['Dialog'],
    },
  });

describe('InfoModal', () => {
  test('mount renders hidden dialog', async () => {
    const wrapper = mountInfoModal();

    const dialog = wrapper.getComponent({ name: 'Dialog' });
    expect(wrapper.getComponent({ name: 'Dialog' }).attributes().visible).toBe(
      'false'
    );
    expect(wrapper.getComponent({ name: 'Dialog' }).attributes().modal).toBe(
      'true'
    );
  });

  test('clicking span sets dialog to visible', async () => {
    const wrapper = mountInfoModal();

    wrapper.get('span').trigger('click');

    await flushPromises();
    const dialog = wrapper.getComponent({ name: 'Dialog' });
    expect(wrapper.getComponent({ name: 'Dialog' }).attributes().visible).toBe(
      'true'
    );
    expect(wrapper.getComponent({ name: 'Dialog' }).attributes().modal).toBe(
      'true'
    );
  });

  test('setting displayModal on open modal to false closes to modal', async () => {
    const wrapper = mountInfoModal();
    const wrapperVm = wrapper.vm as unknown as typeof InfoModal;
    const dialog = wrapper.getComponent({ name: 'Dialog' });
    wrapper.get('span').trigger('click');
    await flushPromises();

    expect(wrapper.getComponent({ name: 'Dialog' }).attributes().visible).toBe(
      'true'
    );
    wrapperVm.displayModal = false;
    await flushPromises();
    expect(wrapper.getComponent({ name: 'Dialog' }).attributes().visible).toBe(
      'false'
    );
  });
});
