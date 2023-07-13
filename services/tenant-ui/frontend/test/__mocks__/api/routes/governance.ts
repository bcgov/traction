import { rest } from 'msw';

import { API_PATH } from '@/helpers/constants';
import { governanceResponse } from '../responses';
import { fullPathWithProxyTenant } from './utils/utils';

export const successHandlers = [
  rest.get(
    fullPathWithProxyTenant(API_PATH.SCHEMA_STORAGE),
    (req, res, ctx) => {
      return res(ctx.status(200), ctx.json(governanceResponse.schemas));
    }
  ),
  rest.get(
    fullPathWithProxyTenant(API_PATH.CREDENTIAL_DEFINITION_STORAGE),
    (req, res, ctx) => {
      return res(
        ctx.status(200),
        ctx.json(governanceResponse.credentialDefinitions)
      );
    }
  ),
  rest.get(
    fullPathWithProxyTenant(API_PATH.CREDENTIAL_DEFINITIONS) + '/:id',
    (req, res, ctx) => {
      return res(
        ctx.status(200),
        ctx.json(governanceResponse.createCredentialDefinition)
      );
    }
  ),
  rest.get(fullPathWithProxyTenant(API_PATH.OCAS), (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(governanceResponse.ocas));
  }),
  rest.get(fullPathWithProxyTenant(API_PATH.OCAS) + '/:id', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(governanceResponse.oca));
  }),
  rest.post(fullPathWithProxyTenant(API_PATH.SCHEMAS), (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(governanceResponse.createSchema));
  }),
  rest.post(
    fullPathWithProxyTenant(API_PATH.SCHEMA_STORAGE),
    (req, res, ctx) => {
      return res(ctx.status(200), ctx.json(governanceResponse.copySchema));
    }
  ),
  rest.post(
    fullPathWithProxyTenant(API_PATH.CREDENTIAL_DEFINITIONS),
    (req, res, ctx) => {
      return res(
        ctx.status(200),
        ctx.json(governanceResponse.createCredentialDefinition)
      );
    }
  ),
  rest.post(fullPathWithProxyTenant(API_PATH.OCAS), (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(governanceResponse.createOca));
  }),
  rest.delete(
    fullPathWithProxyTenant(API_PATH.SCHEMA_STORAGE_ITEM('test-uuid')),
    (req, res, ctx) => {
      return res(ctx.status(200), ctx.json(governanceResponse.deleteResponse));
    }
  ),
  rest.delete(
    fullPathWithProxyTenant(
      API_PATH.CREDENTIAL_DEFINITION_STORAGE_ITEM('test-uuid')
    ),
    (req, res, ctx) => {
      return res(ctx.status(200), ctx.json(governanceResponse.deleteResponse));
    }
  ),
  rest.delete(
    fullPathWithProxyTenant(API_PATH.OCA('test-uuid')),
    (req, res, ctx) => {
      return res(ctx.status(200), ctx.json(governanceResponse.deleteResponse));
    }
  ),
];

export const unknownErrorHandlers = [
  rest.get(
    fullPathWithProxyTenant(API_PATH.SCHEMA_STORAGE),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
  rest.get(
    fullPathWithProxyTenant(API_PATH.CREDENTIAL_DEFINITION_STORAGE),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
  rest.get(
    fullPathWithProxyTenant(API_PATH.CREDENTIAL_DEFINITIONS) + '/:id',
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
  rest.get(fullPathWithProxyTenant(API_PATH.OCAS), (req, res, ctx) => {
    return res(ctx.status(500), ctx.json({}));
  }),
  rest.get(fullPathWithProxyTenant(API_PATH.OCAS) + '/:id', (req, res, ctx) => {
    return res(ctx.status(500), ctx.json({}));
  }),
  rest.post(fullPathWithProxyTenant(API_PATH.SCHEMAS), (req, res, ctx) => {
    return res(ctx.status(500), ctx.json({}));
  }),
  rest.post(
    fullPathWithProxyTenant(API_PATH.SCHEMA_STORAGE),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
  rest.post(
    fullPathWithProxyTenant(API_PATH.CREDENTIAL_DEFINITIONS),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
  rest.post(fullPathWithProxyTenant(API_PATH.OCAS), (req, res, ctx) => {
    return res(ctx.status(500), ctx.json({}));
  }),
  rest.delete(
    fullPathWithProxyTenant(API_PATH.SCHEMA_STORAGE_ITEM('test-uuid')),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
  rest.delete(
    fullPathWithProxyTenant(
      API_PATH.CREDENTIAL_DEFINITION_STORAGE_ITEM('test-uuid')
    ),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
  rest.delete(
    fullPathWithProxyTenant(API_PATH.OCA('test-uuid')),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
];
