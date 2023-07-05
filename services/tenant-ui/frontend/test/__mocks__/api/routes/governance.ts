import { rest } from 'msw';

import { API_PATH } from '@/helpers/constants';
import { governanceResponse } from '../responses';
import { fullPathWithProxyTenant } from './utils/utils';

export const successHandlers = [
  rest.post(fullPathWithProxyTenant(API_PATH.SCHEMAS), (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(governanceResponse.createResponse));
  }),
  rest.get(
    fullPathWithProxyTenant(API_PATH.SCHEMA_STORAGE),
    (req, res, ctx) => {
      return res(
        ctx.status(200),
        ctx.json(governanceResponse.listStoredSchemas)
      );
    }
  ),
];

export const unknownErrorHandlers = [
  rest.post(fullPathWithProxyTenant(API_PATH.SCHEMAS), (req, res, ctx) => {
    return res(ctx.status(500), ctx.json({}));
  }),
  rest.get(
    fullPathWithProxyTenant(API_PATH.SCHEMA_STORAGE),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
];
