import { rest } from 'msw';

import { API_PATH } from '@/helpers/constants';
import { tenantResponse } from '../responses';
import { fullPathWithProxyTenant } from './utils/utils';

export const successHandlers = [
  rest.get(fullPathWithProxyTenant(API_PATH.TENANT_SELF), (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(tenantResponse.self));
  }),
  rest.get(fullPathWithProxyTenant(API_PATH.TENANT_CONFIG), (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(tenantResponse.config));
  }),
  rest.get(fullPathWithProxyTenant(API_PATH.LEDGER_TAA), (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(tenantResponse.taa));
  }),
  rest.get(
    fullPathWithProxyTenant(API_PATH.TENANT_ENDORSER_INFO),
    (req, res, ctx) => {
      return res(ctx.status(200), ctx.json(tenantResponse.endorserInfo));
    }
  ),
  rest.get(
    fullPathWithProxyTenant(API_PATH.TENANT_ENDORSER_CONNECTION),
    (req, res, ctx) => {
      return res(ctx.status(200), ctx.json(tenantResponse.endorserConnection));
    }
  ),
  rest.get(
    fullPathWithProxyTenant(API_PATH.WALLET_DID_PUBLIC),
    (req, res, ctx) => {
      return res(ctx.status(200), ctx.json(tenantResponse.publicDid));
    }
  ),
  rest.get(fullPathWithProxyTenant(API_PATH.TENANT_WALLET), (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(tenantResponse.getTenantSubWallet));
  }),
  rest.post(
    fullPathWithProxyTenant(API_PATH.TENANT_ENDORSER_CONNECTION),
    (req, res, ctx) => {
      return res(ctx.status(200), ctx.json(tenantResponse.connectToEndorser));
    }
  ),
];
