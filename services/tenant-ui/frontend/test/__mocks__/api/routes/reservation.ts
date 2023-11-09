import { http, HttpResponse } from 'msw';

import { API_PATH } from '@/helpers/constants';
import { reservationResponse } from '../responses';
import { fullPathWithProxyTenant } from './utils/utils';

export const successHandlers = [
  http.get(
    fullPathWithProxyTenant(API_PATH.MULTITENANCY_RESERVATION('test-id')),
    () => HttpResponse.json(reservationResponse.reservation)
  ),
  http.post(
    fullPathWithProxyTenant(API_PATH.MULTITENANCY_RESERVATIONS),
    async ({ request }) => {
      const body: any = await request.json();
      if (body.auto_approve)
        return HttpResponse.json(
          reservationResponse.makeReservationAutoApprove
        );
      else return HttpResponse.json(reservationResponse.makeReservationVerify);
    }
  ),
  http.post(
    fullPathWithProxyTenant(
      API_PATH.MULTITENANCY_RESERVATION_CHECK_IN('reservation_id')
    ),
    () => HttpResponse.json(reservationResponse.checkIn)
  ),
  http.post(API_PATH.EMAIL_CONFIRMATION, () => HttpResponse.json({})),
];

export const unknownErrorHandlers = [
  http.get(
    fullPathWithProxyTenant(API_PATH.MULTITENANCY_RESERVATION('test-id')),
    () => HttpResponse.json({}, { status: 500 })
  ),
  http.post(
    fullPathWithProxyTenant(
      API_PATH.MULTITENANCY_RESERVATION_CHECK_IN('reservation_id')
    ),
    () => HttpResponse.json({}, { status: 500 })
  ),
  http.post(fullPathWithProxyTenant(API_PATH.MULTITENANCY_RESERVATIONS), () =>
    HttpResponse.json({}, { status: 500 })
  ),
];
