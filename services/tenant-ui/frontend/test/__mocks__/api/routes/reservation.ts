import { rest } from 'msw';

import { API_PATH } from '@/helpers/constants';
import { reservationResponse } from '../responses';
import { fullPathWithProxyTenant } from './utils/utils';

export const successHandlers = [
  rest.get(
    fullPathWithProxyTenant(API_PATH.MULTITENANCY_RESERVATION('test-id')),
    (req, res, ctx) => {
      return res(ctx.status(200), ctx.json(reservationResponse.reservation));
    }
  ),
  rest.post(
    fullPathWithProxyTenant(API_PATH.MULTITENANCY_RESERVATIONS),
    async (req, res, ctx) => {
      const body = await req.json();
      if (body.auto_approve) {
        return res(
          ctx.status(200),
          ctx.json(reservationResponse.makeReservationAutoApprove)
        );
      } else {
        return res(
          ctx.status(200),
          ctx.json(reservationResponse.makeReservationVerify)
        );
      }
    }
  ),
  rest.post(
    fullPathWithProxyTenant(
      API_PATH.MULTITENANCY_RESERVATION_CHECK_IN('reservation_id')
    ),
    (req, res, ctx) => {
      return res(ctx.status(200), ctx.json(reservationResponse.checkIn));
    }
  ),
  rest.post(API_PATH.EMAIL_CONFIRMATION, (req, res, ctx) => {
    return res(ctx.status(200), ctx.json({}));
  }),
];

export const unknownErrorHandlers = [
  rest.get(
    fullPathWithProxyTenant(API_PATH.MULTITENANCY_RESERVATION('test-id')),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
  rest.post(
    fullPathWithProxyTenant(
      API_PATH.MULTITENANCY_RESERVATION_CHECK_IN('reservation_id')
    ),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
  rest.post(
    fullPathWithProxyTenant(API_PATH.MULTITENANCY_RESERVATIONS),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
];
