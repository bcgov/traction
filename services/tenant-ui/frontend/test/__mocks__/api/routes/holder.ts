import { http, HttpResponse } from 'msw';

import { API_PATH } from '@/helpers/constants';
import { holderResponse } from '../responses';
import { fullPathWithProxyTenant } from './utils/utils';

export const successHandlers = [
  http.get(fullPathWithProxyTenant(API_PATH.CREDENTIALS), () =>
    HttpResponse.json(holderResponse.credentials)
  ),
  http.post(
    fullPathWithProxyTenant(
      API_PATH.ISSUE_CREDENTIAL_RECORDS_SEND_REQUEST('test-id')
    ),
    () => HttpResponse.json(holderResponse.issueCredentialSendRequest)
  ),
  http.delete(
    fullPathWithProxyTenant(API_PATH.ISSUE_CREDENTIAL_RECORD('test-id')),
    () => HttpResponse.json({})
  ),
];

export const unknownErrorHandlers = [
  http.get(fullPathWithProxyTenant(API_PATH.CREDENTIALS), () =>
    HttpResponse.json({}, { status: 500 })
  ),
  http.post(
    fullPathWithProxyTenant(
      API_PATH.ISSUE_CREDENTIAL_RECORDS_SEND_REQUEST('test-id')
    ),
    () => HttpResponse.json({}, { status: 500 })
  ),
  http.delete(
    fullPathWithProxyTenant(API_PATH.ISSUE_CREDENTIAL_RECORD('test-id')),
    () => HttpResponse.json({}, { status: 500 })
  ),
];
