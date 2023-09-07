import router from '@/router';
import { flushPromises } from '@vue/test-utils';
import { expect, test, vi } from 'vitest';

import { useInnkeeperTokenStore, useTenantStore, useTokenStore } from '@/store';

vi.mock('@/router', async () => {
  const router = await vi.importActual<typeof import('@/router')>('@/router');

  return {
    ...router,
  };
});

test('/logout clears token and tenant data', async () => {
  const tokenStore = useTokenStore();
  const tenantStore = useTenantStore();
  router.push('/');
  await router.isReady();

  router.push({ path: '/logout' });
  await flushPromises();

  expect(tokenStore.clearToken).toHaveBeenCalled();
  expect(tenantStore.clearTenant).toHaveBeenCalled();
});

test('/innkeeper/logout clears innkeeper token', async () => {
  const tokenStore = useInnkeeperTokenStore();
  router.push('/');
  await router.isReady();

  router.push({ path: '/innkeeper/logout' });
  await flushPromises();

  expect(tokenStore.clearToken).toHaveBeenCalled();
});

test('non-logout path does not clear any token or tenant data', async () => {
  const innkeeperTokenStore = useInnkeeperTokenStore();
  const tokenStore = useTokenStore();
  const tenantStore = useTenantStore();
  router.push('/');
  await router.isReady();

  router.push({ path: '/issuance/credentials' });
  await flushPromises();

  expect(innkeeperTokenStore.clearToken).toHaveBeenCalled();
  expect(tokenStore.clearToken).toHaveBeenCalled();
  expect(tenantStore.clearTenant).toHaveBeenCalled();
});
