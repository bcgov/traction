import { shallowMount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test, vi } from 'vitest';
import VueToastificationPlugin from 'vue-toastification';

import QRCode from '@/components/common/QRCode.vue';

Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn().mockImplementation(() => Promise.resolve()),
  },
});

const writeTextSpy = vi.spyOn(navigator.clipboard, 'writeText');

const mountQRCode = () =>
  shallowMount(QRCode, {
    props: {
      qrContent: 'test',
    },
    global: {
      plugins: [PrimeVue, VueToastificationPlugin],
    },
  });

describe('QRCode', () => {
  test('toast and copy_to_clipboard called when button clicked', async () => {
    const wrapper = mountQRCode();
    const wrapperVm = wrapper.vm as unknown as typeof QRCode;
    const toastSpy = vi.spyOn(wrapperVm.toast, 'info');

    wrapper.getComponent({ name: 'Button' }).trigger('click');

    expect(toastSpy).toHaveBeenCalled();
    expect(writeTextSpy).toHaveBeenCalled();
  });
});
