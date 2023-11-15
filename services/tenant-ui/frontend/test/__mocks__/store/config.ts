import { vi } from 'vitest';

import { API_PATH } from '@/helpers/constants';

const store: { [key: string]: any } = {
  config: {
    frontend: {
      ux: {
        appTitle: 'Tenant UI',
        aboutBusiness: {
          linkTitle: 'About Business',
          link: 'http://link.com',
          imageUrl: 'http://image.com',
        },
      },
      oidc: {
        active: false,
      },
      tenantProxyPath: API_PATH.TEST_TENANT_PROXY,
      showOIDCReservationLogin: false,
      showInnkeeperAdminLogin: true,
      showWritableComponents: true,
      session: {
        timeoutSeconds: '600',
        countdownSeconds: '30',
      },
    },
    image: {
      tag: '1.0',
      version: '1.0',
      buildtime: '2021-01-01',
    },
    // These mocks are used for storeToRefs in the components
    value: {
      frontend: {
        ux: {
          appTitle: 'Tenant UI',
          aboutBusiness: {
            linkTitle: 'About Business',
            link: 'http://link.com',
            imageUrl: 'http://image.com',
          },
        },
        oidc: {
          authority: 'authority',
        },
        tenantProxyPath: API_PATH.TEST_TENANT_PROXY,
        session: {
          timeoutSeconds: '3600',
          countdownSeconds: '10',
        },
      },
    },
  },
  getPluginList: vi
    .fn()
    .mockResolvedValue(['aries_cloudagent.holder', 'aries_cloudagent.ledger']),
};

export { store };
