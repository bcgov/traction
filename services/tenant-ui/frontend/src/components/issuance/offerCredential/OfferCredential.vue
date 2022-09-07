<template>
  <div>
    <Button
      :disabled="!isIssuer"
      label="Offer Credential"
      icon="pi pi-arrow-up-right"
      @click="openOfferPopup"
    />
    <Dialog
      v-model:visible="displayOfferModal"
      header="Offer Credential"
      :modal="true"
    >
      <OfferCredentialForm />
    </Dialog>
  </div>
</template>

<script setup lang="ts">
// Vue
import { ref } from 'vue';
// PrimeVue
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
// State
import {
  useContactsStore,
  useGovernanceStore,
  useTenantStore,
} from '../../../store';
import { storeToRefs } from 'pinia';
// Custom Components
import OfferCredentialForm from './OfferCredentialForm.vue';
// Other Imports
import { useToast } from 'vue-toastification';

// State setup
const contactsStore = useContactsStore();
const governanceStore = useGovernanceStore();

const toast = useToast();

const { isIssuer } = storeToRefs(useTenantStore());

// -----------------------------------------------------------------------
// Display popup
// ---------------------------------------------------------------------
const displayOfferModal = ref(false);
const openOfferPopup = async () => {
  // Kick of the loading asyncs in the store to fetch contacts/creds
  Promise.all([
    contactsStore.listContacts(),
    governanceStore.listSchemaTemplates(),
  ]).catch((err) => {
    console.error(err);
    toast.error(
      `An error occurred loading your contacts or credentials: ${err}`
    );
  });
  displayOfferModal.value = true;
};
// ---------------------------------------------------------------/display
</script>
