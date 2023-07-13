import { rest } from 'msw';

import { API_PATH } from '@/helpers/constants';
import { tokenResponse } from '../responses';

export const successHandlers = [
  rest.post(API_PATH.MULTITENANCY_WALLET_TOKEN('username'), (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(tokenResponse.token));
  }),
];

export const unknownErrorHandlers = [
  rest.post(API_PATH.MULTITENANCY_WALLET_TOKEN('username'), (req, res, ctx) => {
    return res(ctx.status(500), ctx.json({}));
  }),
];
