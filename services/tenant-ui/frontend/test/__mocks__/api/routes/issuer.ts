import { http, HttpResponse } from 'msw';

import { API_PATH } from '@/helpers/constants';
import { issuerResponse } from '../responses';
import { fullPathWithProxyTenant } from './utils/utils';

export const successHandlers = [
  http.get(fullPathWithProxyTenant(API_PATH.ISSUE_CREDENTIAL_20_RECORDS), () =>
    HttpResponse.json(issuerResponse.credentials)
  ),
  http.get(
    fullPathWithProxyTenant(API_PATH.ISSUE_CREDENTIAL_20_RECORDS) + '/:id',
    () => HttpResponse.json(issuerResponse.credential)
  ),
  http.post(
    fullPathWithProxyTenant(API_PATH.ISSUE_CREDENTIALS_20_SEND_OFFER),
    () => HttpResponse.json(issuerResponse.sendOffer)
  ),
  http.post(fullPathWithProxyTenant(API_PATH.REVOCATION_REVOKE), () =>
    HttpResponse.json({})
  ),
  http.delete(
    fullPathWithProxyTenant(API_PATH.ISSUE_CREDENTIAL_20_RECORD('test-id')),
    () => HttpResponse.json({})
  ),
];

export const unknownErrorHandlers = [
  http.get(fullPathWithProxyTenant(API_PATH.ISSUE_CREDENTIAL_20_RECORDS), () =>
    HttpResponse.json({}, { status: 500 })
  ),
  http.get(
    fullPathWithProxyTenant(API_PATH.ISSUE_CREDENTIAL_20_RECORDS) + '/:id',
    () => HttpResponse.json({}, { status: 500 })
  ),
  http.post(
    fullPathWithProxyTenant(API_PATH.ISSUE_CREDENTIALS_20_SEND_OFFER),
    () => HttpResponse.json({}, { status: 500 })
  ),
  http.post(fullPathWithProxyTenant(API_PATH.REVOCATION_REVOKE), () =>
    HttpResponse.json({}, { status: 500 })
  ),
  http.delete(
    fullPathWithProxyTenant(API_PATH.ISSUE_CREDENTIAL_20_RECORD('test-id')),
    () => HttpResponse.json({}, { status: 500 })
  ),
];
