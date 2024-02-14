<!-- eslint-disable vue/multi-word-component-names -->
<template>
  <v-timeline direction="vertical" side="end">
    <v-timeline-item width="100%">
      <div>
        <v-btn prepend-icon="mdi-email" :disabled="isCreateInviteDisabled" @click="getInvitation">
          Create invite
        </v-btn>
        <div v-if="appStore.invitation">
          <v-textarea
            variant="outlined"
            class="pt-2 fullwidth"
            readonly
            no-resize
            :value="JSON.stringify(appStore.invitation)"
          >
            <template v-slot:append>
              <v-container class="pa-0 d-flex flex-column">
                <v-btn
                  flat
                  icon="mdi-close-circle"
                  @click="() => appStore.setInvitation(undefined)"
                ></v-btn>
              </v-container>
            </template>
          </v-textarea>
          <v-btn variant="text" prepend-icon="mdi-content-copy" @click="copyToClipboard"
            >Copy</v-btn
          >
        </div>
      </div>
    </v-timeline-item>
    <v-timeline-item width="100%">
      <div>
        <v-btn
          prepend-icon="mdi-email-open"
          :disabled="isAcceptInviteDisabled"
          @click="invitationDisplayed = !invitationDisplayed"
        >
          Accept invite
        </v-btn>
        <div v-if="invitationDisplayed">
          <v-textarea
            variant="outlined"
            class="pt-2 fullwidth"
            no-resize
            v-model="invitation"
            :disabled="isAcceptInviteDisabled"
          >
            <template v-slot:append>
              <v-container class="pa-0 d-flex flex-column">
                <v-btn flat icon="mdi-close-circle" @click="clearInvitation"></v-btn>
              </v-container>
            </template>
          </v-textarea>
          <v-btn variant="text" prepend-icon="mdi-send" @click="acceptInvitation">Send</v-btn>
        </div>
      </div>
    </v-timeline-item>
    <v-timeline-item>
      <div>
        <v-btn
          prepend-icon="mdi-send"
          :disabled="isSendRpcRequestDisabled"
          @click="drpcRequestsDisplayed = !drpcRequestsDisplayed"
        >
          Send RPC Request
        </v-btn>
        <div v-if="drpcRequestsDisplayed">
          <v-select
            variant="outlined"
            class="pt-2 fullwidth"
            label="RPC Request Type"
            :items="[
              { type: 'valid', label: 'A valid reqeust' },
              { type: 'invalid', label: 'An invalid request' },
              { type: 'notification', label: 'A notification' }
            ]"
            item-title="label"
            item-value="type"
            v-model="drpcRequestType"
          />
          <v-select
            variant="outlined"
            class="mt-n4"
            label="Connection"
            :items="appStore.connections"
            item-title="connection_id"
            item-value="connection_id"
            v-model="drpcRequestConnection"
          />
          <v-btn variant="text" prepend-icon="mdi-send" @click="sendDrpcRequest">Send</v-btn>
        </div>
      </div>
    </v-timeline-item>
    <v-timeline-item>
      <div>
        <v-btn prepend-icon="mdi-send" :disabled="isSendRpcResponseDisabled">
          Send RPC Response
        </v-btn>
        <div v-if="drpcResponsesDisplayed">
          <v-btn variant="text" prepend-icon="mdi-send" @click="null">Send</v-btn>
        </div>
      </div>
    </v-timeline-item>
  </v-timeline>
</template>

<script setup lang="ts">
import type AgentService from '@/services/agent'
import { useAppStore } from '@/stores/app'
import { computed, inject } from 'vue'

const agentService: AgentService | undefined = inject('agentService')

const appStore = useAppStore()

const invitationDisplayed = defineModel('invitationDisplayed', { default: false })
const invitation = defineModel('invitation', { default: '' })
const drpcRequestsDisplayed = defineModel('drpcRequestsDisplayed', { default: false })
const drpcRequestType = defineModel('drpcRequestType', { default: '' })
const drpcRequestConnection = defineModel('drpcRequestConnection', { default: '' })
const drpcResponsesDisplayed = defineModel('drpcResponsesDisplayed', { default: false })

const isCreateInviteDisabled = computed(() => {
  return !appStore.tenant
})

const isAcceptInviteDisabled = computed(() => {
  return !appStore.tenant
})

const isSendRpcRequestDisabled = computed(() => {
  return !appStore.connections.length
})

const isSendRpcResponseDisabled = computed(() => {
  return !Object.keys(appStore.drpcRequests).length
})

const getInvitation = async () => {
  const oob = await agentService?.fetchInvitation()
  appStore.setInvitation(oob.invitation)
}

const copyToClipboard = () => {
  navigator.clipboard.writeText(JSON.stringify(appStore.invitation))
}

const acceptInvitation = async () => {
  if (!invitation.value) {
    return
  }
  await agentService?.createConnection(invitation.value)
  clearInvitation()
}

const clearInvitation = () => {
  invitationDisplayed.value = false
  invitation.value = ''
}

const sendDrpcRequest = async () => {
  if (!drpcRequestType.value || !drpcRequestConnection.value) {
    return
  }
  let rpcRequest
  switch (drpcRequestType.value) {
    case 'valid':
      rpcRequest = [
        {
          id: '1',
          jsonrpc: '2.0',
          method: 'add',
          params: [1, 2]
        },
        {
          id: '2',
          jsonrpc: '2.0',
          method: 'subtract',
          params: [2, 1]
        }
      ]
      break
    case 'invalid':
      rpcRequest = {
        id: '3',
        jsonrpc: '2.0',
        method: 'rpc.method',
        params: {}
      }
      break
    case 'notification':
      rpcRequest = {
        jsonrpc: '2.0',
        method: 'notify',
        params: { messsage: 'Hello World!' }
      }
      break
  }
  await agentService?.sendDrpcRequest(drpcRequestConnection.value, rpcRequest)
  clearDrpcRequest()
}

const clearDrpcRequest = () => {
  drpcRequestsDisplayed.value = false
  drpcRequestType.value = ''
  drpcRequestConnection.value = ''
}
</script>

<style scoped>
:deep(.v-input__append) {
  padding: 0;
}
</style>
