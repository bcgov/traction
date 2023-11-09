import { http, HttpResponse } from 'msw';

import { API_PATH } from '@/helpers/constants';
import { configResponse } from '../responses';
import { fullPathWithProxyTenant } from './utils/utils';

export const successHandlers = [
  http.get(API_PATH.CONFIG, () => HttpResponse.json(configResponse.config)),
  http.get(fullPathWithProxyTenant(API_PATH.SERVER_PLUGINS), () =>
    HttpResponse.json(configResponse.plugins)
  ),
];

export const unknownErrorHandlers = [
  http.get(API_PATH.CONFIG, () => HttpResponse.json({}, { status: 500 })),
];
