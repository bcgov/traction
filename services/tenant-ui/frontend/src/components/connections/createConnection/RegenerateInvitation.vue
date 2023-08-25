<template>
  <Button
    :title="$t('connect.invitations.regenerate')"
    icon="pi pi-link"
    class="p-button-rounded p-button-icon-only p-button-text"
    @click="openModal"
  />
  <Dialog
    v-model:visible="displayModal"
    :header="$t('connect.invitations.regenerate')"
    :modal="true"
    :style="{ minWidth: '400px' }"
    @update:visible="handleClose"
  >
    <div v-if="loadingItem" class="flex justify-content-center">
      <ProgressSpinner />
    </div>
    <div v-else-if="invitation">
      <!-- Alias -->
      <div class="field w-full">
        <label for="alias">{{ $t('connect.invitation.alias') }}</label>
        <InputText
          :value="invitation.alias"
          class="w-full"
          name="alias"
          readonly
        />
      </div>

      <QRCode :qr-content="invitation.invitation_url" />
    </div>
  </Dialog>
</template>

<script setup lang="ts">
// Vue
import { ref, PropType } from 'vue';
// PrimeVue etc
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import ProgressSpinner from 'primevue/progressspinner';
import { useToast } from 'vue-toastification';
// State
import { storeToRefs } from 'pinia';
import { useConnectionStore } from '@/store';
// Other Components
import QRCode from '../../common/QRCode.vue';

const toast = useToast();

const connectionStore = useConnectionStore();
const { loadingItem } = storeToRefs(useConnectionStore());

// Props
const props = defineProps({
  connectionId: {
    type: String as PropType<string>,
    required: true,
  },
});

// Display popup, fetch and display invitation
const displayModal = ref(false);
const invitation: any = ref(null);
const openModal = async () => {
  displayModal.value = true;
  try {
    invitation.value = await connectionStore.getInvitation(props.connectionId);
  } catch (err) {
    console.error(err);
    toast.error(`Failure getting invitation: ${err}`);
  }
};
const handleClose = async () => {
  displayModal.value = false;
};
</script>
