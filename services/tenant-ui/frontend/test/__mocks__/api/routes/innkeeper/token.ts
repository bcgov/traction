import { rest } from 'msw';

import { API_PATH } from '@/helpers/constants';
import { innkeeperTokenResponse } from '../../responses';
import { fullPathWithProxyTenant } from '../utils/utils';

export const successHandlers = [
  rest.post(
    fullPathWithProxyTenant(API_PATH.MULTITENANCY_TENANT_TOKEN('admin')),
    (req, res, ctx) => {
      return res(ctx.status(200), ctx.json(innkeeperTokenResponse.login));
    }
  ),
];

export const unknownErrorHandlers = [
  rest.post(
    fullPathWithProxyTenant(API_PATH.MULTITENANCY_TENANT_TOKEN('admin')),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
];
