import { rest } from 'msw';

import { API_PATH } from '@/helpers/constants';
import { reservationResponse } from '../responses';
import { fullPathWithProxyTenant } from './utils/utils';

export const successHandlers = [
  rest.post(
    fullPathWithProxyTenant(API_PATH.MULTITENANCY_RESERVATIONS),
    (req, res, ctx) => {
      return res(
        ctx.status(200),
        ctx.json(reservationResponse.makeReservation)
      );
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
];

export const unknownErrorHandlers = [
  rest.post(
    fullPathWithProxyTenant(API_PATH.MULTITENANCY_RESERVATIONS),
    (req, res, ctx) => {
      return res(ctx.status(500), ctx.json({}));
    }
  ),
];
