<template>
  <form @submit.prevent="handleSubmit()">
    <!-- Alias -->
    <div class="field">
      <label for="create_contact_alias">Contact Alias</label>
      <InputText
        v-model="create_contact_alias"
        type="text"
        name="create_contact_alias"
        autofocus
        :readonly="!!invitation_url"
      />
    </div>

    <div v-if="invitation_url">
      <!-- QR Code Display -->
      <QRCode :qr-content="invitation_url" />

      <Button label="Close" class="mt-5 w-full" @click="$emit('closed')" />
    </div>
    <Button v-else type="submit" label="Submit" class="mt-5 w-full" />
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import { useToast } from 'vue-toastification';
import QRCode from '../../common/QRCode.vue';
import { useContactsStore } from '../../../store';

const contactsStore = useContactsStore();

// For notifications
const toast = useToast();

// To store local data
const create_contact_alias = ref('');
const invitation_url = ref('');

// ----------------------------------------------------------------
// Creating a new contact
// ----------------------------------------------------------------
const emit = defineEmits(['closed', 'success']);

// Form submission
const handleSubmit = async () => {
  try {
    // call store
    const result = await contactsStore.createInvitation(
      create_contact_alias.value
    );
    if (result != null && result['invitation_url']) {
      invitation_url.value = result['invitation_url'];
      console.log(`invitation_url: ${invitation_url.value}`);
      toast.info('Contact Created');
      emit('success');
    }
    return false;
  } catch (error) {
    toast.error(`Failure: ${error}`);
  }
};

// ---------------------------------------------------/create contact
</script>
