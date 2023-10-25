<template>
  <form v-if="urlEntryStep" @submit.prevent="handleSubmit(!v$.$invalid)">
    <!-- Invitation type -->
    <div class="mb-3">
      <span>{{ $t('connect.invitation.type') }}</span>
      <div class="my-2">
        <RadioButton
          v-model="isOob"
          input-id="type1"
          name="type"
          :value="false"
        />
        <label for="type1" class="ml-2">{{
          $t('connect.invitation.typeConnections')
        }}</label>
      </div>
      <div>
        <RadioButton
          v-model="isOob"
          input-id="type2"
          name="type"
          :value="true"
        />
        <label for="type2" class="ml-2">{{
          $t('connect.invitation.typeOob')
        }}</label>
      </div>
    </div>

    <div class="field">
      <div class="flex justify-content-between">
        <label
          for="inviteUrl"
          :class="{ 'p-error': v$.inviteUrl.$invalid && submitted }"
        >
          {{ $t('connect.acceptInvitation.url') }}
        </label>
        <Button
          :label="$t('connect.acceptInvitation.skipUrl')"
          class="p-button-link flex justify-content-end pt-1 pr-0"
          @click="skipUrl"
        />
      </div>

      <div class="p-inputgroup">
        <InputText
          id="inviteUrl"
          v-model="v$.inviteUrl.$model"
          :class="{ 'p-invalid': v$.inviteUrl.$invalid && submitted }"
        />
        <Button type="submit" icon="pi pi-arrow-right" />
      </div>

      <span v-if="v$.inviteUrl.$error && submitted">
        <span v-for="(error, index) of v$.inviteUrl.$errors" :key="index">
          <small class="p-error block">{{ error.$message }}</small>
        </span>
      </span>
      <small v-else-if="v$.inviteUrl.$invalid && submitted" class="p-error">{{
        v$.inviteUrl.required.$message
      }}</small>
    </div>

    <div class="mb-4">
      <i class="pi pi-info-circle"></i>
      {{ $t('connect.acceptInvitation.supportedUrl') }}
      <strong>
        <code>
          {{
            $t('connect.acceptInvitation.supportedUrlEx', [
              isOob ? 'oob' : 'c_i',
            ])
          }}
        </code>
      </strong>
    </div>
  </form>

  <AcceptInviteSubmission
    v-else
    :invitation-string="invitationString"
    :is-oob="isOob"
    @closed="$emit('closed')"
  />
</template>

<script setup lang="ts">
// Vue
import { reactive, ref } from 'vue';
// PrimeVue / Validation
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import RadioButton from 'primevue/radiobutton';
import { required, url } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { useToast } from 'vue-toastification';
// Components
import AcceptInviteSubmission from './AcceptInviteSubmission.vue';
import { paramFromUrlString } from '@/helpers';

const toast = useToast();

defineEmits(['closed']);

const urlEntryStep = ref(true);
const invitationString = ref('{}');
const isOob = ref(false);

// Skip URL enter
const skipUrl = () => {
  urlEntryStep.value = false;
};

// Validation
const formFields = reactive({
  inviteUrl: '',
});
const rules = {
  inviteUrl: { required, url },
};
const v$ = useVuelidate(rules, formFields);

// URL Form submission
const submitted = ref(false);
const handleSubmit = async (isFormValid: boolean) => {
  submitted.value = true;

  if (!isFormValid) {
    return;
  }

  try {
    const inviteParam = paramFromUrlString(
      formFields.inviteUrl,
      isOob.value ? 'oob' : 'c_i'
    ) as string;
    if (!inviteParam) {
      throw Error('Invalid format for invitation URL');
    }
    invitationString.value = window.atob(inviteParam);
    urlEntryStep.value = false;
  } catch (error) {
    toast.error(`Failure: ${error}`);
  } finally {
    submitted.value = false;
  }
};
</script>
