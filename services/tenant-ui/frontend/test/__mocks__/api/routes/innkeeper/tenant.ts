import { http, HttpResponse } from 'msw';

import { API_PATH } from '@/helpers/constants';
import { innkeeperTenantResponse } from '../../responses';
import { fullPathWithProxyTenant } from '../utils/utils';

export const successHandlers = [
  http.get(fullPathWithProxyTenant(API_PATH.INNKEEPER_RESERVATIONS), () =>
    HttpResponse.json(innkeeperTenantResponse.reservations)
  ),
  http.get(fullPathWithProxyTenant(API_PATH.INNKEEPER_TENANTS), () =>
    HttpResponse.json(innkeeperTenantResponse.tenants)
  ),
  http.put(
    fullPathWithProxyTenant(API_PATH.INNKEEPER_RESERVATIONS_APPROVE('test-id')),
    () => HttpResponse.json(innkeeperTenantResponse.approveReservation)
  ),
  http.put(
    fullPathWithProxyTenant(API_PATH.INNKEEPER_RESERVATIONS_DENY('test-id')),
    () => HttpResponse.json(innkeeperTenantResponse.denyReservation)
  ),
  http.put(
    fullPathWithProxyTenant(API_PATH.INNKEEPER_TENANT_CONFIG('test-id')),
    () => HttpResponse.json(innkeeperTenantResponse.updateTenant)
  ),
];

export const unknownErrorHandlers = [
  http.get(fullPathWithProxyTenant(API_PATH.INNKEEPER_RESERVATIONS), () =>
    HttpResponse.json({}, { status: 500 })
  ),
  http.get(fullPathWithProxyTenant(API_PATH.INNKEEPER_TENANTS), () =>
    HttpResponse.json({}, { status: 500 })
  ),
  http.put(
    fullPathWithProxyTenant(API_PATH.INNKEEPER_RESERVATIONS_APPROVE('test-id')),
    () => HttpResponse.json({}, { status: 500 })
  ),
  http.put(
    fullPathWithProxyTenant(API_PATH.INNKEEPER_RESERVATIONS_DENY('test-id')),
    () => HttpResponse.json({}, { status: 500 })
  ),
  http.put(
    fullPathWithProxyTenant(API_PATH.INNKEEPER_TENANT_CONFIG('test-id')),
    () => HttpResponse.json({}, { status: 500 })
  ),
];
