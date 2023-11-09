import { http, HttpResponse } from 'msw';

import { API_PATH } from '@/helpers/constants';
import { tenantResponse } from '../responses';
import { fullPathWithProxyTenant } from './utils/utils';

export const successHandlers = [
  http.get(fullPathWithProxyTenant(API_PATH.TENANT_SELF), () =>
    HttpResponse.json(tenantResponse.self)
  ),
  http.get(fullPathWithProxyTenant(API_PATH.TENANT_CONFIG), () =>
    HttpResponse.json(tenantResponse.config)
  ),
  http.get(fullPathWithProxyTenant(API_PATH.LEDGER_TAA), () =>
    HttpResponse.json(tenantResponse.taa)
  ),
  http.get(fullPathWithProxyTenant(API_PATH.TENANT_ENDORSER_INFO), () =>
    HttpResponse.json(tenantResponse.endorserInfo)
  ),
  http.get(fullPathWithProxyTenant(API_PATH.TENANT_ENDORSER_CONNECTION), () =>
    HttpResponse.json(tenantResponse.endorserConnection)
  ),
  http.get(fullPathWithProxyTenant(API_PATH.WALLET_DID_PUBLIC), () =>
    HttpResponse.json(tenantResponse.publicDid)
  ),
  http.get(fullPathWithProxyTenant(API_PATH.TENANT_WALLET), () =>
    HttpResponse.json(tenantResponse.getTenantSubWallet)
  ),
  http.post(fullPathWithProxyTenant(API_PATH.TENANT_ENDORSER_CONNECTION), () =>
    HttpResponse.json(tenantResponse.connectToEndorser)
  ),
  http.put(fullPathWithProxyTenant(API_PATH.TENANT_WALLET), () =>
    HttpResponse.json(tenantResponse.updateWallet)
  ),
];

export const unknownErrorHandlers = [
  http.get(fullPathWithProxyTenant(API_PATH.TENANT_SELF), () =>
    HttpResponse.json({}, { status: 500 })
  ),
  http.get(fullPathWithProxyTenant(API_PATH.TENANT_CONFIG), () =>
    HttpResponse.json({}, { status: 500 })
  ),
  http.get(fullPathWithProxyTenant(API_PATH.LEDGER_TAA), () =>
    HttpResponse.json({}, { status: 500 })
  ),
  http.get(fullPathWithProxyTenant(API_PATH.TENANT_ENDORSER_INFO), () =>
    HttpResponse.json({}, { status: 500 })
  ),
  http.get(fullPathWithProxyTenant(API_PATH.TENANT_ENDORSER_CONNECTION), () =>
    HttpResponse.json({}, { status: 500 })
  ),
  http.get(fullPathWithProxyTenant(API_PATH.WALLET_DID_PUBLIC), () =>
    HttpResponse.json({}, { status: 500 })
  ),
  http.get(fullPathWithProxyTenant(API_PATH.TENANT_WALLET), () =>
    HttpResponse.json({}, { status: 500 })
  ),
  http.post(fullPathWithProxyTenant(API_PATH.TENANT_ENDORSER_CONNECTION), () =>
    HttpResponse.json({}, { status: 500 })
  ),
  http.put(fullPathWithProxyTenant(API_PATH.TENANT_WALLET), () =>
    HttpResponse.json({}, { status: 500 })
  ),
];
