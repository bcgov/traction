import { http, HttpResponse } from 'msw';

import { API_PATH } from '@/helpers/constants';
import { governanceResponse } from '../responses';
import { fullPathWithProxyTenant } from './utils/utils';

export const successHandlers = [
  http.get(fullPathWithProxyTenant(API_PATH.SCHEMA_STORAGE), () =>
    HttpResponse.json(governanceResponse.schemas)
  ),
  http.get(
    fullPathWithProxyTenant(API_PATH.CREDENTIAL_DEFINITION_STORAGE),
    () => HttpResponse.json(governanceResponse.credentialDefinitions)
  ),
  http.get(
    fullPathWithProxyTenant(API_PATH.CREDENTIAL_DEFINITIONS) + '/:id',
    () => HttpResponse.json(governanceResponse.createCredentialDefinition)
  ),
  http.get(fullPathWithProxyTenant(API_PATH.OCAS), () =>
    HttpResponse.json(governanceResponse.ocas)
  ),
  http.get(fullPathWithProxyTenant(API_PATH.OCAS) + '/:id', () =>
    HttpResponse.json(governanceResponse.oca)
  ),
  http.post(fullPathWithProxyTenant(API_PATH.SCHEMAS), () =>
    HttpResponse.json(governanceResponse.createSchema)
  ),
  http.post(fullPathWithProxyTenant(API_PATH.SCHEMA_STORAGE), () =>
    HttpResponse.json(governanceResponse.copySchema)
  ),
  http.post(fullPathWithProxyTenant(API_PATH.CREDENTIAL_DEFINITIONS), () =>
    HttpResponse.json(governanceResponse.createCredentialDefinition)
  ),
  http.post(fullPathWithProxyTenant(API_PATH.OCAS), () =>
    HttpResponse.json(governanceResponse.createOca)
  ),
  http.delete(
    fullPathWithProxyTenant(API_PATH.SCHEMA_STORAGE_ITEM('test-uuid')),
    () => HttpResponse.json(governanceResponse.deleteResponse)
  ),
  http.delete(
    fullPathWithProxyTenant(
      API_PATH.CREDENTIAL_DEFINITION_STORAGE_ITEM('test-uuid')
    ),
    () => HttpResponse.json(governanceResponse.deleteResponse)
  ),
  http.delete(fullPathWithProxyTenant(API_PATH.OCA('test-uuid')), () =>
    HttpResponse.json(governanceResponse.deleteResponse)
  ),
];

export const unknownErrorHandlers = [
  http.get(fullPathWithProxyTenant(API_PATH.SCHEMA_STORAGE), () =>
    HttpResponse.json({}, { status: 500 })
  ),
  http.get(
    fullPathWithProxyTenant(API_PATH.CREDENTIAL_DEFINITION_STORAGE),
    () => HttpResponse.json({}, { status: 500 })
  ),
  http.get(
    fullPathWithProxyTenant(API_PATH.CREDENTIAL_DEFINITIONS) + '/:id',
    () => {
      HttpResponse.json({}, { status: 500 });
    }
  ),
  http.get(fullPathWithProxyTenant(API_PATH.OCAS), () =>
    HttpResponse.json({}, { status: 500 })
  ),
  http.get(fullPathWithProxyTenant(API_PATH.OCAS) + '/:id', () =>
    HttpResponse.json({}, { status: 500 })
  ),
  http.post(fullPathWithProxyTenant(API_PATH.SCHEMAS), () =>
    HttpResponse.json({}, { status: 500 })
  ),
  http.post(fullPathWithProxyTenant(API_PATH.SCHEMA_STORAGE), () =>
    HttpResponse.json({}, { status: 500 })
  ),
  http.post(fullPathWithProxyTenant(API_PATH.CREDENTIAL_DEFINITIONS), () =>
    HttpResponse.json({}, { status: 500 })
  ),
  http.post(fullPathWithProxyTenant(API_PATH.OCAS), () =>
    HttpResponse.json({}, { status: 500 })
  ),
  http.delete(
    fullPathWithProxyTenant(API_PATH.SCHEMA_STORAGE_ITEM('test-uuid')),
    () => HttpResponse.json({}, { status: 500 })
  ),
  http.delete(
    fullPathWithProxyTenant(
      API_PATH.CREDENTIAL_DEFINITION_STORAGE_ITEM('test-uuid')
    ),
    () => HttpResponse.json({}, { status: 500 })
  ),
  http.delete(fullPathWithProxyTenant(API_PATH.OCA('test-uuid')), () =>
    HttpResponse.json({}, { status: 500 })
  ),
];
