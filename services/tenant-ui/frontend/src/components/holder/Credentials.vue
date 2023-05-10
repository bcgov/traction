<template>
  <div class="flex justify-content-between mb-3">
    <div class="flex justify-content-start">
      <h3 class="mt-0">
        <span v-if="cardView">{{ $t('common.credentials') }}</span>
        <span v-else>{{ $t('credentials.exchanges.exchanges') }}</span>
      </h3>
    </div>
    <div class="flex justify-content-end">
      <Button
        v-if="cardView"
        icon="pi pi-table"
        title="View in Table format"
        text
        rounded
        aria-label="Filter"
        @click="cardView = false"
      />
      <Button
        v-else
        icon="pi pi-th-large"
        title="View in Card format"
        text
        rounded
        aria-label="Filter"
        @click="cardView = true"
      />

      <Button
        icon="pi pi-refresh"
        title="Refresh Credentials list"
        text
        rounded
        aria-label="Filter"
        @click="loadCredentials"
      />
    </div>
  </div>

  <CredentialsCards
    v-if="cardView"
    @accept="acceptOffer"
    @delete="deleteCredential"
    @reject="rejectOffer"
  />
  <CredentialsTable
    v-else
    @accept="acceptOffer"
    @delete="deleteCredential"
    @reject="rejectOffer"
  />
</template>

<script setup lang="ts">
// Types
import {
  CredAttrSpec,
  V10CredentialExchange,
} from '@/types/acapyApi/acapyInterface';

// Vue
import { ref } from 'vue';
// PrimeVue etc
import Button from 'primevue/button';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'vue-toastification';
// State
import { useContactsStore, useHolderStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other components
import CredentialsCards from './CredentialsCards.vue';
import CredentialsTable from './CredentialsTable.vue';

const toast = useToast();
const confirm = useConfirm();

// State
const contactsStore = useContactsStore();
const { contacts } = storeToRefs(useContactsStore());
const holderStore = useHolderStore();

// Table/card view toggle
const cardView = ref(false);

// Actions for a cred row/card
const acceptOffer = (event: any, data: V10CredentialExchange) => {
  if (data.credential_exchange_id) {
    holderStore.acceptCredentialOffer(data.credential_exchange_id).then(() => {
      toast.success(`Credential successfully added to your wallet`);
    });
  }
};
const rejectOffer = (event: any, data: V10CredentialExchange) => {
  confirm.require({
    target: event.currentTarget,
    message: 'Are you sure you want to reject this credential offer?',
    header: 'Confirmation',
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      if (data.credential_exchange_id) {
        holderStore
          .deleteCredentialExchange(data.credential_exchange_id)
          .then(() => {
            loadCredentials();
            toast.success(`Credential offer rejected`);
          });
      }
    },
  });
};
const deleteCredential = (event: any, data: V10CredentialExchange) => {
  confirm.require({
    target: event.currentTarget,
    message: 'Are you sure you want to delete this credential exchange record?',
    header: 'Confirmation',
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      if (data.credential_exchange_id) {
        holderStore
          .deleteCredentialExchange(data.credential_exchange_id)
          .then(() => {
            loadCredentials();
            toast.info(`Credential exchange deleted`);
          });
      }
    },
  });
};

// Get the credential exchange list
const loadCredentials = async () => {
  holderStore.listHolderCredentialExchanges().catch((err) => {
    console.error(err);
    toast.error(`Failure: ${err}`);
  });
};
</script>
