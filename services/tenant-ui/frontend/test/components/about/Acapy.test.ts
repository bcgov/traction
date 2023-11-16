import { useTenantStore } from '@/store';
import { createTestingPinia } from '@pinia/testing';
import { mount } from '@vue/test-utils';
import PrimeVue from 'primevue/config';
import { describe, expect, test, vi } from 'vitest';

import Acapy from '@/components/about/Acapy.vue';

// Mocks
vi.mock('vue-router');

const mockRouter = async (name = 'test') => {
  const routerMock = await import('vue-router');
  routerMock.useRoute = vi.fn().mockReturnValue({
    name,
  });
  routerMock.useRouter = vi.fn().mockReturnValue({
    push: vi.fn(),
  });
};

const createWrapper = () =>
  mount(Acapy, {
    global: {
      plugins: [PrimeVue, createTestingPinia()],
    },
  });

describe('Acapy', async () => {
  test('mount matches snapshot with expected values', async () => {
    await mockRouter();
    const tenantStore = useTenantStore();
    expect(createWrapper().html()).toMatchSnapshot();
    expect(tenantStore.getServerConfig).toHaveBeenCalled();
  });
});
