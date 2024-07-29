import { http, HttpResponse } from 'msw';
import { API_PATH } from '@/helpers/constants';
import { verifierResponse } from '../responses';
import { fullPathWithProxyTenant } from './utils/utils';

export const successHandlers = [
  http.get(fullPathWithProxyTenant(API_PATH.PRESENT_PROOF_20_RECORDS), () =>
    HttpResponse.json(verifierResponse.presentProofRecords)
  ),
  http.post(
    fullPathWithProxyTenant(API_PATH.PRESENT_PROOF_20_SEND_REQUEST),
    () => HttpResponse.json(verifierResponse.presentProofSendRequest)
  ),
  http.delete(
    fullPathWithProxyTenant(API_PATH.PRESENT_PROOF_20_RECORD('test-uuid')),
    () => HttpResponse.json({})
  ),
];

export const unknownErrorHandlers = [
  http.get(fullPathWithProxyTenant(API_PATH.PRESENT_PROOF_20_RECORDS), () =>
    HttpResponse.json({}, { status: 500 })
  ),
  http.post(
    fullPathWithProxyTenant(API_PATH.PRESENT_PROOF_20_SEND_REQUEST),
    () => HttpResponse.json({}, { status: 500 })
  ),
  http.delete(
    fullPathWithProxyTenant(API_PATH.PRESENT_PROOF_20_RECORD('test-uuid')),
    () => HttpResponse.json({}, { status: 500 })
  ),
];
