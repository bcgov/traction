import { config } from '@vue/test-utils';
import { vi } from 'vitest';

// If you looking for the holder store it isn't mocked here because it has the same function names
// as issuer and verifier stores and merging them into one object would cause conflicts.
import {
  commonStore,
  configStore,
  connectionStore,
  governanceStore,
  // holderStore: See comment above
  issuerStore,
  messageStore,
  reservationStore,
  tenantStore,
  tokenStore,
  verifierStore,
  // Innkeeper
  innkeeperOidcStore,
  innkeeperTenantsStore,
  innkeeperTokenStore,
  // oidc
  oidcStore,
} from './__mocks__/store';

// Add mocks used in many files here. The mocks can be overridden in individual files if needed.

// Fully mock pinia with a copy of pinia's actual implementation and override the storeToRefs method to include mock of all stores.
vi.mock('pinia', async () => {
  const pinia = await vi.importActual<typeof import('pinia')>('pinia');

  return {
    ...pinia,
    storeToRefs: vi.fn(() =>
      Object.assign(
        commonStore,
        configStore,
        connectionStore,
        governanceStore,
        // holderStore: See comment above
        issuerStore,
        messageStore,
        reservationStore,
        tenantStore,
        tokenStore,
        verifierStore,
        // Innkeeper
        innkeeperOidcStore,
        innkeeperTenantsStore,
        innkeeperTokenStore,
        // oidc
        oidcStore
      )
    ),
  };
});

vi.mock('@/store', () => ({
  useCommonStore: vi.fn(() => commonStore),
  useConfigStore: vi.fn(() => configStore),
  useConnectionStore: vi.fn(() => connectionStore),
  useGovernanceStore: vi.fn(() => governanceStore),
  // useHolderStore: vi.fn(() => holderStore), // See comment above
  useIssuerStore: vi.fn(() => issuerStore),
  useMessageStore: vi.fn(() => messageStore),
  useReservationStore: vi.fn(() => reservationStore),
  useTenantStore: vi.fn(() => tenantStore),
  useTokenStore: vi.fn(() => tokenStore),
  useVerifierStore: vi.fn(() => verifierStore),
  // Innkeeper
  useInnkeeperOidcStore: vi.fn(() => innkeeperOidcStore),
  useInnkeeperTenantsStore: vi.fn(() => innkeeperTenantsStore),
  useInnkeeperTokenStore: vi.fn(() => innkeeperTokenStore),
  // oidc
  useOidcStore: vi.fn(() => oidcStore),
}));

vi.mock('vue-i18n', () => ({
  useI18n: vi.fn(() => ({
    locale: vi.fn(() => 'en'),
    t: vi.fn((key: string) => key),
  })),
}));

// Global mocks which are not imported
config.global.mocks = {
  $t: vi.fn((key: string) => key),
};
