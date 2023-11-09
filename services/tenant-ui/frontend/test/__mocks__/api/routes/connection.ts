import { HttpResponse, http } from 'msw';

import { API_PATH } from '@/helpers/constants';
import { connectionResponse } from '../responses';
import { fullPathWithProxyTenant } from './utils/utils';

export const successHandlers = [
  http.get(fullPathWithProxyTenant(API_PATH.CONNECTIONS), () =>
    HttpResponse.json(connectionResponse.listConnections)
  ),
  http.get(fullPathWithProxyTenant(API_PATH.CONNECTIONS) + '/:id', () =>
    HttpResponse.json(connectionResponse.getConnection)
  ),
  http.get(
    fullPathWithProxyTenant(API_PATH.CONNECTIONS_INVITATION('test-uuid')),
    () => HttpResponse.json(connectionResponse.getConnectionInvitation)
  ),
  http.post(
    fullPathWithProxyTenant(API_PATH.CONNECTIONS_CREATE_INVITATION),
    () => HttpResponse.json(connectionResponse.createConnection)
  ),
  http.post(
    fullPathWithProxyTenant(API_PATH.CONNECTIONS_RECEIVE_INVITATION),
    () => HttpResponse.json(connectionResponse.receiveInvitation)
  ),
  http.post(fullPathWithProxyTenant(API_PATH.DID_EXCHANGE_CREATE_REQUEST), () =>
    HttpResponse.json(connectionResponse.didExchange)
  ),
  http.put(fullPathWithProxyTenant(API_PATH.CONNECTION('test-uuid')), () =>
    HttpResponse.json(connectionResponse.getConnection)
  ),
  http.delete(fullPathWithProxyTenant(API_PATH.CONNECTION('test-uuid')), () =>
    HttpResponse.json({})
  ),
];

export const unknownErrorHandlers = [
  http.get(fullPathWithProxyTenant(API_PATH.CONNECTIONS), () =>
    HttpResponse.json({}, { status: 500 })
  ),
  http.get(fullPathWithProxyTenant(API_PATH.CONNECTIONS) + '/:id', () =>
    HttpResponse.json({}, { status: 500 })
  ),
  http.get(
    fullPathWithProxyTenant(API_PATH.CONNECTIONS_INVITATION('test-uuid')),
    () => HttpResponse.json({}, { status: 500 })
  ),
  http.post(
    fullPathWithProxyTenant(API_PATH.CONNECTIONS_CREATE_INVITATION),
    () => {
      return HttpResponse.json({}, { status: 500 });
    }
  ),
  http.post(
    fullPathWithProxyTenant(API_PATH.CONNECTIONS_RECEIVE_INVITATION),
    () => {
      return HttpResponse.json({}, { status: 500 });
    }
  ),
  http.post(fullPathWithProxyTenant(API_PATH.DID_EXCHANGE_CREATE_REQUEST), () =>
    HttpResponse.json({}, { status: 500 })
  ),
  http.put(fullPathWithProxyTenant(API_PATH.CONNECTION('test-uuid')), () =>
    HttpResponse.json({}, { status: 500 })
  ),
  http.delete(fullPathWithProxyTenant(API_PATH.CONNECTION('test-uuid')), () =>
    HttpResponse.json({}, { status: 500 })
  ),
];
