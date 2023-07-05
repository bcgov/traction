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
      ariesDetails: {
        acapyVersion: '1.0',
        ledger: 'ledger',
        ledgerName: 'ledgerName',
        ledgerBrowser: 'ledgerBrowser',
        tailsServer: 'tailsServer',
      },
      tenantProxyPath: API_PATH.TEST_TENANT_PROXY,
    },
    image: {
      tag: '1.0',
      version: '1.0',
      buildtime: '2021-01-01',
    },
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
        ariesDetails: {
          acapyVersion: '1.0',
          ledger: 'ledger',
          ledgerName: 'ledgerName',
          ledgerBrowser: 'ledgerBrowser',
          tailsServer: 'tailsServer',
        },
        oidc: {
          authority: 'authority',
        },
        tenantProxyPath: API_PATH.TEST_TENANT_PROXY,
      },
    },
  },
};

export { store };
