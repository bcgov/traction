import { API_PATH } from '@/helpers/constants';

export function fullPathWithProxyTenant(prefix: string) {
  return API_PATH.TEST_TENANT_PROXY + prefix;
}
