import type { TenantData } from '@/types/tenant.data'

export default class Tenant {
  private tenant_name: string
  private wallet_id: string

  token: string

  constructor(data: TenantData) {
    this.tenant_name = data.tenant_name
    this.wallet_id = data.wallet_id

    this.token = data.token
  }

  get tenantName() {
    return this.tenant_name
  }

  get walletId() {
    return this.wallet_id
  }
}
