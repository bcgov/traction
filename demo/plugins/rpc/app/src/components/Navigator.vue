<!-- eslint-disable vue/multi-word-component-names -->
<template>
    <v-timeline direction="vertical" side="end">
        <v-timeline-item width="100%">
            <div>
                <v-btn prepend-icon="mdi-email" variant="outlined" :disabled="isCreateInviteDisabled"
                    @click="getInvitation">
                    Create invite
                </v-btn>
                <v-textarea v-if="appStore.invitation" variant="outlined" class="pt-2 fullwidth" readonly no-resize
                    :value="JSON.stringify(appStore.invitation)">
                    <template v-slot:append>
                        <v-container class="pa-0 d-flex flex-column">
                            <v-btn flat icon="mdi-close-circle" @click="() => appStore.setInvitation(undefined)"></v-btn>
                            <v-btn flat icon="mdi-content-copy" @click="copyToClipboard"></v-btn>
                        </v-container>
                    </template>
                </v-textarea>
            </div>
        </v-timeline-item>
        <v-timeline-item width="100%">
            <div>
                <v-btn prepend-icon="mdi-email-open" variant="outlined" :disabled="isAcceptInviteDisabled"
                    @click="invitationDisplayed = !invitationDisplayed">
                    Accept invite
                </v-btn>
                <v-textarea v-if="invitationDisplayed" variant="outlined" class="pt-2 fullwidth" no-resize
                    v-model="invitation" :disabled="isAcceptInviteDisabled">
                    <template v-slot:append>
                        <v-container class="pa-0 d-flex flex-column">
                            <v-btn flat icon="mdi-close-circle" @click="clearInvitation"></v-btn>
                            <v-btn flat icon="mdi-send" @click="acceptInvitation"></v-btn>
                        </v-container>
                    </template>
                </v-textarea>
            </div>
        </v-timeline-item>
        <v-timeline-item>
            <div>
                <v-btn prepend-icon="mdi-send" variant="outlined" disabled>
                    Send RPC Request
                </v-btn>
            </div>
        </v-timeline-item>
        <v-timeline-item>
            <div>
                <v-btn prepend-icon="mdi-send" variant="outlined" disabled>
                    Send RPC Response
                </v-btn>
            </div>
        </v-timeline-item>
    </v-timeline>
</template>

<script setup lang="ts">
import type AgentService from '@/services/agent';
import { useAppStore } from '@/stores/app';
import { computed, inject } from 'vue';

const agentService: AgentService | undefined = inject('agentService');

const appStore = useAppStore();

const invitationDisplayed = defineModel('invitationDisplayed', { default: false });
const invitation = defineModel('invitation', {default: ''});

const isCreateInviteDisabled = computed(() => {
    return !appStore.tenant;
});

const isAcceptInviteDisabled = computed(() => {
    return !appStore.tenant;
});

const getInvitation = async () => {
    const oob = await agentService?.fetchInvitation();
    appStore.setInvitation(oob.invitation);
};

const copyToClipboard = () => {
    navigator.clipboard.writeText(JSON.stringify(appStore.invitation));
};

const acceptInvitation = async () => {
    if (!invitation.value) {
        return;
    }
    await agentService?.createConnection(invitation.value);
    clearInvitation();
};

const clearInvitation = () => {
    invitationDisplayed.value = false;
    invitation.value = '';
}
</script>

<style scoped>
:deep(.v-input__append) {
    padding: 0;
}
</style>