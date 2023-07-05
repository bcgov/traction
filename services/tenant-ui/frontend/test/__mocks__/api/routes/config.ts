import { rest } from 'msw';

import { API_PATH } from '@/helpers/constants';
import { configResponse } from '../responses';
import { fullPathWithProxyTenant } from './utils/utils';

export const successHandlers = [
  rest.get(API_PATH.CONFIG, (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(configResponse.get));
  }),
  rest.get(
    fullPathWithProxyTenant(API_PATH.SERVER_PLUGINS),
    (req, res, ctx) => {
      return res(ctx.status(200), ctx.json(configResponse.plugins));
    }
  ),
];

export const unknownErrorHandlers = [
  rest.get(API_PATH.CONFIG, (req, res, ctx) => {
    return res(ctx.status(500), ctx.json({}));
  }),
];
