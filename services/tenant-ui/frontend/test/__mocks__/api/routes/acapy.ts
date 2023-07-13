import { rest } from 'msw';

import { API_PATH } from '@/helpers/constants';
import { acapyResponse } from '../responses';

export const successHandlers = [
  rest.all(API_PATH.TEST_TENANT_PROXY, (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(acapyResponse.basic));
  }),
];

export const authErrorHandlers = [
  rest.all(API_PATH.TEST_TENANT_PROXY, (req, res, ctx) => {
    return res(
      ctx.status(401),
      ctx.json({
        reason: `Test: ${req.headers.get('Authorization')}`,
      })
    );
  }),
];

export const unknownErrorHandlers = [
  rest.all(API_PATH.TEST_TENANT_PROXY, (req, res, ctx) => {
    return res(ctx.status(500), ctx.json({}));
  }),
];
