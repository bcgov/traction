import { http, HttpResponse } from 'msw';

import { API_PATH } from '@/helpers/constants';
import { innkeeperTokenResponse } from '../../responses';
import { fullPathWithProxyTenant } from '../utils/utils';

export const successHandlers = [
  http.post(
    fullPathWithProxyTenant(API_PATH.MULTITENANCY_TENANT_TOKEN('admin')),
    () => HttpResponse.json(innkeeperTokenResponse.login)
  ),
];

export const unknownErrorHandlers = [
  http.post(
    fullPathWithProxyTenant(API_PATH.MULTITENANCY_TENANT_TOKEN('admin')),
    () => HttpResponse.json({}, { status: 500 })
  ),
];
