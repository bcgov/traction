import { rest } from 'msw';

import { API_PATH } from '@/helpers/constants';
import { issuerResponse } from '../responses';
import { fullPathWithProxyTenant } from './utils/utils';

export const successHandlers = [
  rest.get(
    fullPathWithProxyTenant(API_PATH.ISSUE_CREDENTIAL_RECORDS),
    (req, res, ctx) => {
      return res(ctx.status(200), ctx.json(issuerResponse.credentials));
    }
  ),
  rest.get(
    fullPathWithProxyTenant(API_PATH.ISSUE_CREDENTIAL_RECORDS) + '/:id',
    (req, res, ctx) => {
      return res(ctx.status(200), ctx.json(issuerResponse.credential));
    }
  ),
  rest.post(
    fullPathWithProxyTenant(API_PATH.ISSUE_CREDENTIALS_SEND_OFFER),
    (req, res, ctx) => {
      return res(ctx.status(200), ctx.json(issuerResponse.sendOffer));
    }
  ),
  rest.post(
    fullPathWithProxyTenant(API_PATH.REVOCATION_REVOKE),
    (req, res, ctx) => {
      return res(ctx.status(200), ctx.json({}));
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
  rest.get(
    fullPathWithProxyTenant(API_PATH.ISSUE_CREDENTIAL_RECORDS),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
  rest.get(
    fullPathWithProxyTenant(API_PATH.ISSUE_CREDENTIAL_RECORDS) + '/:id',
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
  rest.post(
    fullPathWithProxyTenant(API_PATH.ISSUE_CREDENTIALS_SEND_OFFER),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
  rest.post(
    fullPathWithProxyTenant(API_PATH.REVOCATION_REVOKE),
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
