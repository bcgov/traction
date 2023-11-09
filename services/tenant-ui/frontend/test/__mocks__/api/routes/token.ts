import { http, HttpResponse } from 'msw';

import { API_PATH } from '@/helpers/constants';
import { tokenResponse } from '../responses';

export const successHandlers = [
  http.post(API_PATH.MULTITENANCY_WALLET_TOKEN('username'), () =>
    HttpResponse.json(tokenResponse.token)
  ),
];

export const unknownErrorHandlers = [
  http.post(API_PATH.MULTITENANCY_WALLET_TOKEN('username'), () =>
    HttpResponse.json({}, { status: 500 })
  ),
];
