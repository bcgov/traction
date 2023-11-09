import { http, HttpResponse } from 'msw';

import { API_PATH } from '@/helpers/constants';
import { acapyResponse } from '../responses';

export const successHandlers = [
  http.all(API_PATH.TEST_TENANT_PROXY, () =>
    HttpResponse.json(acapyResponse.basic)
  ),
];

export const authErrorHandlers = [
  http.all(API_PATH.TEST_TENANT_PROXY, ({ request }) =>
    HttpResponse.json(
      {
        reason: `Test: ${request.headers.get('Authorization')}`,
      },
      {
        status: 401,
      }
    )
  ),
];

export const unknownErrorHandlers = [
  http.all(API_PATH.TEST_TENANT_PROXY, () =>
    HttpResponse.json({}, { status: 500 })
  ),
];
