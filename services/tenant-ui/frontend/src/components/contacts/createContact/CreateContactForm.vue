<template>
  <form @submit.prevent="handleSubmit()">
    <div class="create-contact">
      <h1>Contacts</h1>
      <div>
        <h2>Create Connection Invitation</h2>
        <span class="p-float-label">
          <InputText
            v-model="create_contact_alias"
            type="text"
            name="create_contact_alias"
            autofocus
          />
          <label for="create_contact_alias">Contact Alias</label>
        </span>
      </div>
      <QRCode v-if="invitation_url" :qr-content="invitation_url" />
      <Button
        v-if="invitation_url"
        label="Close"
        class="mt-5 w-full"
        @click="$emit('closed')"
      />
      <Button v-else type="submit" label="Submit" class="mt-5 w-full" />
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import { useToast } from 'vue-toastification';
import QRCode from '../../common/QRCode.vue';
import { useContactsStore } from '../../../store';
import { storeToRefs } from 'pinia';

const contactsStore = useContactsStore();

// use the loading state from the store to disable the button...
const { loading } = storeToRefs(useContactsStore());

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

<style scoped>
.create-contact {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  margin: 10px;
  padding: 15px;
  border: 3px solid grey;
  border-radius: 8px;
}

span.p-float-label {
  margin: 25px;
}
</style>
