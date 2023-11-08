import { http, HttpResponse } from 'msw';

import { API_PATH } from '@/helpers/constants';
import { messageResponse } from '../responses';
import { fullPathWithProxyTenant } from './utils/utils';

export const successHandlers = [
  http.post(
    fullPathWithProxyTenant(API_PATH.BASICMESSAGES_SEND('connId')),
    () => HttpResponse.json({ test: 'test' })
  ),
  http.get(fullPathWithProxyTenant(API_PATH.BASICMESSAGES), () =>
    HttpResponse.json(messageResponse.messages)
  ),
];

export const unknownErrorHandlers = [
  http.post(
    fullPathWithProxyTenant(API_PATH.BASICMESSAGES_SEND('connId')),
    () => HttpResponse.json({}, { status: 500 })
  ),
];
