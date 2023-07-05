import { rest } from 'msw';

import { API_PATH } from '@/helpers/constants';
import { issuerResponse } from '../responses';
import { fullPathWithProxyTenant } from './utils/utils';

export const successHandlers = [
  rest.get(
    fullPathWithProxyTenant(API_PATH.ISSUE_CREDENTIAL_RECORDS),
    (req, res, ctx) => {
      return res(ctx.status(200), ctx.json(issuerResponse.listCredentials));
    }
  ),
];

export const unknownErrorHandlers = [
  rest.get(
    fullPathWithProxyTenant(API_PATH.ISSUE_CREDENTIAL_RECORDS),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
];
