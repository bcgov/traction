import { rest } from 'msw';

import { API_PATH } from '@/helpers/constants';
import { holderResponse } from '../responses';
import { fullPathWithProxyTenant } from './utils/utils';

export const successHandlers = [
  rest.get(fullPathWithProxyTenant(API_PATH.CREDENTIALS), (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(holderResponse.credentials));
  }),
  rest.post(
    fullPathWithProxyTenant(
      API_PATH.ISSUE_CREDENTIAL_RECORDS_SEND_REQUEST('test-id')
    ),
    (req, res, ctx) => {
      return res(
        ctx.status(200),
        ctx.json(holderResponse.issueCredentialSendRequest)
      );
    }
  ),
  rest.delete(
    fullPathWithProxyTenant(API_PATH.ISSUE_CREDENTIAL_RECORD('test-id')),
    (req, res, ctx) => {
      return res(ctx.status(200), ctx.json({}));
    }
  ),
];

export const unknownErrorHandlers = [
  rest.get(fullPathWithProxyTenant(API_PATH.CREDENTIALS), (req, res, ctx) => {
    return res(ctx.status(500), ctx.json({}));
  }),
  rest.post(
    fullPathWithProxyTenant(
      API_PATH.ISSUE_CREDENTIAL_RECORDS_SEND_REQUEST('test-id')
    ),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
  rest.delete(
    fullPathWithProxyTenant(API_PATH.ISSUE_CREDENTIAL_RECORD('test-id')),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
];
