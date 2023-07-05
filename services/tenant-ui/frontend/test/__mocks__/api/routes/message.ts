import { rest } from 'msw';

import { API_PATH } from '@/helpers/constants';
import { messageResponse } from '../responses';
import { fullPathWithProxyTenant } from './utils/utils';

export const successHandlers = [
  rest.post(
    fullPathWithProxyTenant(API_PATH.BASICMESSAGES_SEND('connId')),
    (req, res, ctx) => {
      return res(ctx.status(200), ctx.json({ test: 'test' }));
    }
  ),
  rest.get(fullPathWithProxyTenant(API_PATH.BASICMESSAGES), (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(messageResponse.get));
  }),
];

export const unknownErrorHandlers = [
  rest.post(
    fullPathWithProxyTenant(API_PATH.BASICMESSAGES_SEND('connId')),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
];
