import { rest } from 'msw';
import { API_PATH } from '@/helpers/constants';
import { verifierResponse } from '../responses';
import { fullPathWithProxyTenant } from './utils/utils';

export const successHandlers = [
  rest.get(
    fullPathWithProxyTenant(API_PATH.PRESENT_PROOF_RECORDS),
    (req, res, ctx) => {
      return res(
        ctx.status(200),
        ctx.json(verifierResponse.presentProofRecords)
      );
    }
  ),
  rest.post(
    fullPathWithProxyTenant(API_PATH.PRESENT_PROOF_SEND_REQUEST),
    (req, res, ctx) => {
      return res(
        ctx.status(200),
        ctx.json(verifierResponse.presentProofSendRequest)
      );
    }
  ),
  rest.delete(
    fullPathWithProxyTenant(API_PATH.PRESENT_PROOF_RECORD('test-uuid')),
    (req, res, ctx) => {
      return res(ctx.status(200), ctx.json({}));
    }
  ),
];

export const unknownErrorHandlers = [
  rest.get(
    fullPathWithProxyTenant(API_PATH.PRESENT_PROOF_RECORDS),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
  rest.post(
    fullPathWithProxyTenant(API_PATH.PRESENT_PROOF_SEND_REQUEST),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
  rest.delete(
    fullPathWithProxyTenant(API_PATH.PRESENT_PROOF_RECORD('test-uuid')),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
];
