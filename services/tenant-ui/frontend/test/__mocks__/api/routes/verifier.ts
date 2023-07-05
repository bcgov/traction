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
  rest.get(
    fullPathWithProxyTenant(API_PATH.PRESENT_PROOF_RECORD('test-uuid')),
    (req, res, ctx) => {
      return res(
        ctx.status(200),
        ctx.json(verifierResponse.presentProofRecord)
      );
    }
  ),
];
