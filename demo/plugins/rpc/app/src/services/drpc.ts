import { useAppStore } from '@/stores/app'
import AgentService from '@/services/agent'

export default class DrpcService {
  private agentService!: AgentService

  private appStore = useAppStore()

  constructor(agentService: AgentService) {
    this.agentService = agentService
  }

  async handleDrpcMessage(topic: string, message: any): Promise<void> {
    // Deep copy the message so we don't modify it when processing
    const messageCopy = JSON.parse(JSON.stringify(message))

    switch (topic) {
      case 'drpc_request':
        this.appStore.addMessage(message)

        // eslint-disable-next-line no-case-declarations
        const {
          request: dRequest,
          connection_id: connectionId,
          thread_id: rpcRequestId
        } = messageCopy
        // eslint-disable-next-line no-case-declarations
        const { request } = dRequest
        // eslint-disable-next-line no-case-declarations
        const aRequest = request && !Array.isArray(request) ? [request] : request

        if (aRequest?.length) {
          const aResult = aRequest.map(this.rpcMethodHandler).filter((result: any) => !!result)
          const response = request && !Array.isArray(request) ? aResult?.[0] ?? {} : aResult
          await this.agentService.sendDrpcResponse(connectionId, rpcRequestId, response)
          this.appStore.addMessage(
            JSON.stringify({
              connection_id: connectionId,
              thread_id: rpcRequestId,
              response: { state: 'completed', response }
            })
          )
        }
        break
      case 'drpc_response':
        // eslint-disable-next-line no-case-declarations
        const { response: dResponse } = messageCopy
        // eslint-disable-next-line no-case-declarations
        const { response } = dResponse
        // eslint-disable-next-line no-case-declarations
        const aResponse = response && !Array.isArray(response) ? [response] : response

        if (aResponse.length) {
          for (const response of aResponse) {
            if (response.result) {
              this.appStore.addMessage(response.result)
            } else if (response.error) {
              this.appStore.addMessage(response.error.message)
            }
          }
        }
        break
      default:
        break
    }
  }

  private rpcMethodHandler(request: any): any {
    const { method, params } = request
    const aParams = params && !Array.isArray(params) ? Object.values(params) : params

    switch (method) {
      case 'sum':
        return {
          id: request.id,
          jsonrpc: '2.0',
          result: aParams.reduce((acc: number, val: number) => (acc += val), 0)
        }
      case 'subtract':
        // eslint-disable-next-line no-case-declarations
        const first = aParams.shift()
        return {
          id: request.id,
          jsonrpc: '2.0',
          result: aParams.reduce((acc: number, val: number) => (acc -= val), first)
        }
      default:
        // eslint-disable-next-line no-case-declarations
        const { id } = request
        if (!id) {
          // Assume its a notification and do nothing
          return
        }
        return {
          id: request.id || null,
          jsonrpc: '2.0',
          error: {
            code: '-32601',
            message: 'Method not found'
          }
        }
    }
  }

  async sendRequest(connectionId: string, request: any): Promise<void> {
    return this.agentService.sendDrpcRequest(connectionId, request)
  }

  async sendResponse(connectionId: string, threadId: string, response: any): Promise<void> {
    return this.agentService.sendDrpcResponse(connectionId, threadId, response)
  }
}
