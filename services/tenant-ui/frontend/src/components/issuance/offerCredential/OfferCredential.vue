<template>
  <div>
    <Button
      :disabled="!isIssuer"
      :label="t('issue.offer')"
      icon="pi pi-arrow-up-right"
      @click="openModal"
    />
    <Dialog
      v-model:visible="displayModal"
      :header="t('issue.offer')"
      :modal="true"
      :style="{ width: '500px' }"
      @update:visible="handleClose"
    >
      <OfferCredentialForm @success="$emit('success')" @closed="handleClose" />
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
import { useI18n } from 'vue-i18n';

// State setup
const contactsStore = useContactsStore();
const governanceStore = useGovernanceStore();

const toast = useToast();
const { t } = useI18n();

const { isIssuer } = storeToRefs(useTenantStore());

// -----------------------------------------------------------------------
// Display popup
// ---------------------------------------------------------------------
defineEmits(['success']);
const displayModal = ref(false);
const openModal = async () => {
  // Kick of the loading asyncs in the store to fetch contacts/creds
  Promise.all([
    contactsStore.listContacts(),
    // governanceStore.listSchemaTemplates(),
    governanceStore.listCredentialTemplates(),
  ]).catch((err) => {
    console.error(err);
    toast.error(
      `An error occurred loading your contacts or credentials: ${err}`
    );
  });
  displayModal.value = true;
};
const handleClose = async () => {
  // some logic... maybe we shouldn't close?
  displayModal.value = false;
};
// ---------------------------------------------------------------/display
</script>
