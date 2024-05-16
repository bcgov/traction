import { useAppStore } from '@/stores/app'
import type AgentService from '@/services/agent'

export default class ConnectionService {
  private agentService!: AgentService
  private appStore = useAppStore()

  constructor(agentService: AgentService) {
    this.agentService = agentService
  }

  handleConnectionMessage(message: any): void {
    const { state } = message
    if (state === 'active') {
      const { their_label: label } = message
      this.appStore.addConnection(message)
      this.appStore.addMessage(`You are now connected with ${label}`)
    }
  }

  async createInvitation(): Promise<any> {
    return this.agentService.fetchInvitation()
  }

  async acceptInvitation(invitation: any): Promise<void> {
    return this.agentService.createConnection(invitation)
  }
}
