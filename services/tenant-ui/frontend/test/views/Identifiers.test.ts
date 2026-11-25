import { flushPromises, shallowMount } from '@vue/test-utils';
import Button from 'primevue/button';
import PrimeVue from 'primevue/config';
import InputText from 'primevue/inputtext';
import { ref } from 'vue';
import { beforeEach, describe, expect, test, vi } from 'vitest';

import { API_PATH } from '@/helpers/constants';
import Identifiers from '@/views/Identifiers.vue';
import { tenantStore } from '../__mocks__/store';

const { postHttp } = vi.hoisted(() => ({ postHttp: vi.fn() }));

vi.mock('pinia', async () => ({
  ...(await vi.importActual<typeof import('pinia')>('pinia')),
  storeToRefs: () => tenantStore,
}));

vi.mock('@/store/acapyApi', () => ({
  useAcapyApi: () => ({ postHttp }),
}));

vi.mock('vue-toastification', () => ({
  useToast: () => ({ success: vi.fn(), error: vi.fn() }),
}));

describe('WebVH DID creation', () => {
  beforeEach(() => {
    postHttp.mockReset().mockResolvedValue({
      data: { did: 'did:webvh:scid:registry.example:billing:issuer' },
    });
    Object.assign(tenantStore, {
      tenantWallet: ref({}),
      loading: ref(false),
      serverConfig: ref({
        config: {
          plugin_config: {
            webvh: { server_url: 'https://registry.example' },
          },
        },
      }),
      webvhConfig: ref({}),
      walletDids: ref([]),
      publicDid: ref(null),
      writeLedger: ref(null),
      getWebvhConfig: vi.fn().mockResolvedValue(undefined),
      getWalletDids: vi.fn().mockResolvedValue(undefined),
      getPublicDid: vi.fn().mockResolvedValue(undefined),
      getWriteLedger: vi.fn().mockResolvedValue(undefined),
    });
  });

  test.each([
    {
      witnesses: ['did:key:witness'],
      witness: { threshold: 1 },
      watchers: ['https://watcher.example'],
    },
    { watchers: ['https://watcher.example'] },
  ])(
    'applies server policy and preserves configured options: %j',
    async (options) => {
      tenantStore.webvhConfig.value = options;
      const wrapper = shallowMount(Identifiers, {
        global: {
          plugins: [PrimeVue],
          renderStubDefaultSlot: true,
          stubs: {
            Button: false,
            InputText: false,
            DataTable: { template: '<div><slot name="header" /></div>' },
            Dialog: {
              props: ['visible'],
              template:
                '<div v-if="visible"><slot /><slot name="footer" /></div>',
            },
          },
        },
      });
      await flushPromises();
      await wrapper.getComponent(Button).trigger('click');
      await wrapper
        .getComponent<typeof InputText>('#dialog-namespace')
        .setValue(' billing ');
      await wrapper
        .getComponent<typeof InputText>('#dialog-alias')
        .setValue(' issuer ');
      const buttons = wrapper.findAllComponents(Button);
      await buttons[buttons.length - 1].trigger('click');
      await flushPromises();

      expect(postHttp).toHaveBeenCalledExactlyOnceWith(
        API_PATH.DID_WEBVH_CREATE,
        {
          options: {
            apply_policy: true,
            identifier: 'issuer',
            namespace: 'billing',
            server_url: 'https://registry.example',
            ...options,
          },
        }
      );
      wrapper.unmount();
    }
  );
});
