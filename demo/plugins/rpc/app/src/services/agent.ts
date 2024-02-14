import { useAppStore } from "@/stores/app";
import Tenant from "@/types/tenant";

export default class AgentService {
    appStore = useAppStore();

    async fetchTenant(): Promise<Tenant> {
        const res = await fetch('/api/tenant', {
            headers: {
                'Content-Type': 'application/json',
            }
        });
        return new Tenant(await res.json());
    }

    async fetchInvitation(): Promise<any> {
        const res = await fetch('/api/invitation', {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.appStore?.tenant?.token}`
            }
        });
        return await res.json();
    }

    async createConnection(invitation: any): Promise<void> {
        const res = await fetch('/api/connection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.appStore?.tenant?.token}`
            },
            body: invitation
        });

        return await res.json();

    }
}