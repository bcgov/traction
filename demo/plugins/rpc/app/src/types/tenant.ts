import type { TenantData } from "@/types/tenant.data";

export default class Tenant {
    #tenant_name: string;
    
    token: string;

    constructor(data: TenantData) {
        this.#tenant_name = data.tenant_name;

        this.token = data.token;
    }

    get tenantName() {
        return this.#tenant_name;
    }
}