<template>
  <form @submit.prevent="handleSubmit(!v$.$invalid)">
    <!-- Comment -->
    <div class="field">
      <label
        for="comment"
        :class="{ 'p-error': v$.comment.$invalid && submitted }"
      >
        {{ t('issue.revoke.comment') }}
      </label>
      <Textarea
        id="comment"
        v-model="v$.comment.$model"
        class="w-full"
        :class="{ 'p-invalid': v$.comment.$invalid && submitted }"
        :auto-resize="true"
        rows="2"
      />
      <span v-if="v$.comment.$error && submitted">
        <span v-for="(error, index) of v$.comment.$errors" :key="index">
          <small class="p-error block">{{ error.$message }}</small>
        </span>
      </span>
      <small v-else-if="v$.comment.$invalid && submitted" class="p-error">{{
        v$.comment.required.$message
      }}</small>
    </div>

    <div class="rev-details">
      <p>
        <small>
          <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
          {{ t('issue.connection') }} {{ props.credExchRecord?.connection }}
        </small>
      </p>
      <p>
        <small>
          <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
          {{ t('issue.revocationId') }}
          {{ props.credExchRecord?.cred_rev_id }}
        </small>
      </p>
      <p>
        <small>
          <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
          {{ t('issue.revocationRegistry') }}
          {{ props.credExchRecord?.rev_reg_id }}
        </small>
      </p>
    </div>
    <Button
      type="submit"
      :label="t('issue.revoke.action')"
      class="mt-5 w-full"
      :disabled="loading"
      :loading="loading"
    />
  </form>
</template>

<script setup lang="ts">
// Types
import { FormattedIssuedCredentialRecord } from '@/helpers/tableFormatters';
import { RevokeRequest } from '@/types/acapyApi/acapyInterface';

// Vue/State
import { reactive, ref } from 'vue';
import { useIssuerStore } from '@/store';
import { storeToRefs } from 'pinia';
// PrimeVue / Validation
import Button from 'primevue/button';
import Textarea from 'primevue/textarea';
import { useVuelidate } from '@vuelidate/core';
import { useToast } from 'vue-toastification';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const issuerStore = useIssuerStore();
const { loading } = storeToRefs(useIssuerStore());

const toast = useToast();

const emit = defineEmits(['closed', 'success']);

// Props
const props = defineProps<{
  credExchRecord: FormattedIssuedCredentialRecord;
  connectionDisplay: string;
}>();

// Validation
const formFields = reactive({
  comment: '',
});
const rules = {
  comment: {},
};
const v$ = useVuelidate(rules, formFields);

// Form submission
const submitted = ref(false);
const handleSubmit = async (isFormValid: boolean) => {
  submitted.value = true;
  if (!isFormValid) {
    return;
  }

  try {
    const payload: RevokeRequest = {
      comment: formFields.comment,
      connection_id: props.credExchRecord.connection_id,
      rev_reg_id: props.credExchRecord.rev_reg_id,
      cred_rev_id: props.credExchRecord.cred_rev_id,
      publish: true,
      notify: true,
    };
    await issuerStore.revokeCredential(payload);
    emit('success');
    // close up on success
    emit('closed');
    toast.success(t('issue.revoke.success'));
  } catch (error) {
    console.error(error);
    toast.error(`Failure: ${error}`);
  } finally {
    submitted.value = false;
  }
};
</script>

<style scoped lang="scss">
.rev-details {
  p {
    margin: 0;
    small {
      word-break: break-all;
    }
  }
}
</style>
