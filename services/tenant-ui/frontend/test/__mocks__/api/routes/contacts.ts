import { rest } from 'msw';

import { API_PATH } from '@/helpers/constants';
import { contactsResponse } from '../responses';
import { fullPathWithProxyTenant } from './utils/utils';

export const successHandlers = [
  rest.get(fullPathWithProxyTenant(API_PATH.CONNECTIONS), (req, res, ctx) =>
    res(ctx.status(200), ctx.json(contactsResponse.listConnections))
  ),
  rest.post(
    fullPathWithProxyTenant(API_PATH.CONNECTIONS_CREATE_INVITATION),
    (req, res, ctx) =>
      res(ctx.status(200), ctx.json(contactsResponse.createConnectionResponse))
  ),
  rest.post(
    fullPathWithProxyTenant(API_PATH.CONNECTIONS_RECEIVE_INVITATION),
    (req, res, ctx) =>
      res(ctx.status(200), ctx.json(contactsResponse.receiveInvitationResponse))
  ),
  rest.delete(
    fullPathWithProxyTenant(API_PATH.CONNECTION('test-uuid')),
    (req, res, ctx) => res(ctx.status(200), ctx.json({}))
  ),
];

export const unknownErrorHandlers = [
  rest.get(fullPathWithProxyTenant(API_PATH.CONNECTIONS), (req, res, ctx) => {
    return res(ctx.status(500), ctx.json({}));
  }),
  rest.post(
    fullPathWithProxyTenant(API_PATH.CONNECTIONS_CREATE_INVITATION),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
  rest.post(
    fullPathWithProxyTenant(API_PATH.CONNECTIONS_RECEIVE_INVITATION),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
  rest.delete(
    fullPathWithProxyTenant(API_PATH.CONNECTION('test-uuid')),
    (req, res, ctx) => res(ctx.status(500), ctx.json({}))
  ),
];
