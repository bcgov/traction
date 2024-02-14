import { useAppStore } from '@/stores/app'
import Tenant from '@/types/tenant'

export default class AgentService {
  appStore = useAppStore()

  async fetchTenant(): Promise<Tenant> {
    const res = await fetch('/api/tenant', {
      headers: {
        'Content-Type': 'application/json'
      }
    })
    return new Tenant(await res.json())
  }

  async fetchInvitation(): Promise<any> {
    const res = await fetch('/api/invitation', {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${this.appStore?.tenant?.token}`
      }
    })
    return await res.json()
  }

  async createConnection(invitation: any): Promise<void> {
    const res = await fetch('/api/connection', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${this.appStore?.tenant?.token}`
      },
      body: invitation
    })

    return await res.json()
  }

  async sendDrpcRequest(connectionId: string, rpcRequest: any): Promise<any> {
    const res = await fetch('/api/drpc/request', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${this.appStore?.tenant?.token}`
      },
      body: JSON.stringify({ connection_id: connectionId, rpc_request: rpcRequest } as any)
    })

    return await res.json()
  }

  async sendDrpcResponse(
    connectionId: string,
    rpcRequestId: string,
    rpcResponse: any
  ): Promise<void> {
    await fetch(`/api/drpc/response`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${this.appStore?.tenant?.token}`
      },
      body: JSON.stringify({
        connection_id: connectionId,
        rpc_request_id: rpcRequestId,
        rpc_response: rpcResponse
      } as any)
    })
  }
}
