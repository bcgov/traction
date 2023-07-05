import { rest } from 'msw';

import { API_PATH } from '@/helpers/constants';
import { innkeeperTenantResponse } from '../../responses';
import { fullPathWithProxyTenant } from '../utils/utils';

export const successHandlers = [
  rest.get(
    fullPathWithProxyTenant(API_PATH.INNKEEPER_RESERVATIONS),
    (req, res, ctx) => {
      return res(
        ctx.status(200),
        ctx.json(innkeeperTenantResponse.reservations)
      );
    }
  ),
  rest.get(
    fullPathWithProxyTenant(API_PATH.INNKEEPER_TENANTS),
    (req, res, ctx) => {
      return res(ctx.status(200), ctx.json(innkeeperTenantResponse.tenants));
    }
  ),
  rest.put(
    fullPathWithProxyTenant(API_PATH.INNKEEPER_RESERVATIONS_APPROVE('test-id')),
    (req, res, ctx) => {
      return res(
        ctx.status(200),
        ctx.json(innkeeperTenantResponse.approveReservation)
      );
    }
  ),
  rest.put(
    fullPathWithProxyTenant(API_PATH.INNKEEPER_RESERVATIONS_DENY('test-id')),
    (req, res, ctx) => {
      return res(
        ctx.status(200),
        ctx.json(innkeeperTenantResponse.denyReservation)
      );
    }
  ),
  rest.put(
    fullPathWithProxyTenant(API_PATH.INNKEEPER_TENANT_CONFIG('test-id')),
    (req, res, ctx) => {
      return res(
        ctx.status(200),
        ctx.json(innkeeperTenantResponse.updateTenant)
      );
    }
  ),
];

export const unknownErrorHandlers = [
  rest.get(
    fullPathWithProxyTenant(API_PATH.INNKEEPER_RESERVATIONS),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
  rest.get(
    fullPathWithProxyTenant(API_PATH.INNKEEPER_TENANTS),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
  rest.put(
    fullPathWithProxyTenant(API_PATH.INNKEEPER_RESERVATIONS_APPROVE('test-id')),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
  rest.put(
    fullPathWithProxyTenant(API_PATH.INNKEEPER_RESERVATIONS_DENY('test-id')),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
  rest.put(
    fullPathWithProxyTenant(API_PATH.INNKEEPER_TENANT_CONFIG('test-id')),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
];
