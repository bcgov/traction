<template>
  <h3 class="mt-0">Credentials (Credential Exchanges)</h3>

  <CredentialsTableFormat
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
import { onMounted, ref } from 'vue';
// PrimeVue etc
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'vue-toastification';
// State
import { useContactsStore, useHolderStore } from '@/store';
import { storeToRefs } from 'pinia';
// Other components
import CredentialsTableFormat from './CredentialsTable.vue';

const toast = useToast();
const confirm = useConfirm();

// State
const contactsStore = useContactsStore();
const { contacts } = storeToRefs(useContactsStore());
const holderStore = useHolderStore();

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

// Get the credential exchange list when loading the component
const loadCredentials = async () => {
  holderStore.listHolderCredentialExchanges().catch((err) => {
    console.error(err);
    toast.error(`Failure: ${err}`);
  });

  // Load contacts if not already there for display
  if (!contacts.value || !contacts.value.length) {
    contactsStore.listContacts().catch((err) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
    });
  }
};

onMounted(async () => {
  loadCredentials();
});
</script>
