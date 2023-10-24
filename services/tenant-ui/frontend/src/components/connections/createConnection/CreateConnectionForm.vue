<template>
  <form @submit.prevent="handleSubmit(!v$.$invalid)">
    <div v-if="!invitation_url">
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

      <!-- Single or multi use connection -->
      <div>{{ $t('connect.invitation.typeSingleMulti') }}</div>
      <div class="my-2">
        <RadioButton
          v-model="multi"
          input-id="sm1"
          name="singleMulti"
          :value="false"
        />
        <label for="sm1" class="ml-2">{{
          $t('connect.invitation.typeSingleUse')
        }}</label>
      </div>
      <RadioButton
        v-model="multi"
        input-id="sm2"
        name="singleMulti"
        :value="true"
      />
      <label for="sm2" class="ml-2">{{
        $t('connect.invitation.typeMultiUse')
      }}</label>
    </div>

    <!-- Alias -->
    <div class="field w-full mt-3">
      <label for="alias" :class="{ 'p-error': v$.alias.$invalid && submitted }">
        {{ $t('connect.invitation.alias') }}
      </label>
      <InputText
        v-model="v$.alias.$model"
        :class="{ 'p-invalid': v$.alias.$invalid && submitted }"
        class="w-full"
        type="text"
        name="alias"
        autofocus
        :readonly="!!invitation_url"
      />
      <small v-if="v$.alias.$invalid && submitted" class="p-error"
        >{{ v$.alias.required.$message }}
      </small>
    </div>

    <!-- OOB Settings -->
    <Panel
      v-if="isOob && !invitation_url"
      class="settings-group mb-5"
      toggleable
      collapsed
    >
      <template #header> {{ $t('connect.invitation.oobSettings') }} </template>
      <!-- Goal -->
      <div class="field w-full">
        <label for="goal">{{ $t('connect.invitation.goal') }}</label>
        <InputText v-model="goal" class="w-full" type="text" name="goal" />
      </div>
      <!-- Goal Code -->
      <div class="field w-full">
        <label for="goal">{{ $t('connect.invitation.goalCode') }}</label>
        <Dropdown
          v-model="goal_code"
          show-clear
          :options="codes"
          option-label="name"
          class="w-full"
        />
      </div>

      <!-- My Label -->
      <div class="field w-full">
        <label for="goal">{{ $t('connect.invitation.myLabel') }}</label>
        <InputText
          v-model="my_label"
          class="w-full"
          type="text"
          name="my_label"
        />
      </div>
    </Panel>

    <div v-if="invitation_url">
      <!-- QR Code Display -->
      <QRCode :qr-content="invitation_url" />

      <Button
        :label="$t('connect.invitation.close')"
        class="mt-5 w-full"
        @click="$emit('closed')"
      />
    </div>
    <Button
      v-else
      type="submit"
      :label="$t('connect.invitation.submit')"
      class="mt-5 w-full"
    />
  </form>
</template>

<script setup lang="ts">
// Vue
import { reactive, ref } from 'vue';
// State
import { useConnectionStore } from '../../../store';
// PrimeVue / Validation
import Button from 'primevue/button';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Panel from 'primevue/panel';
import RadioButton from 'primevue/radiobutton';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { useToast } from 'vue-toastification';
// Other Components
import QRCode from '../../common/QRCode.vue';

const connectionStore = useConnectionStore();

const toast = useToast();

const emit = defineEmits(['closed', 'success']);

// To store local data
const goal = ref('');
const goal_code: any = ref('');
const my_label = ref('');
const multi = ref(false);
const invitation_url = ref('');
const isOob = ref(false);

const codes = ref([
  { name: 'Issue a credential (issue-vc)', code: 'issue-vc' },
  { name: 'Request a proof (request-proof)', code: 'request-proof' },
  {
    name: 'Create an account with a service (create-account)',
    code: 'create-account	',
  },
  {
    name: 'Establish a peer-to-peer messaging relationship (p2p-messaging)',
    code: 'p2p-messaging',
  },
]);

// Validation
const formFields = reactive({
  alias: '',
});
const rules = {
  alias: { required },
};
const v$ = useVuelidate(rules, formFields);

// Create a new connection
const submitted = ref(false);
const handleSubmit = async (isFormValid: boolean) => {
  submitted.value = true;
  if (!isFormValid) {
    return;
  }
  try {
    // call store
    const code = goal_code.value ? goal_code.value.code : '';
    const result = isOob.value
      ? await await connectionStore.createOobInvitation(multi.value, {
          accept: ['didcomm/aip1', 'didcomm/aip2;env=rfc19'],
          alias: formFields.alias,
          goal: goal.value,
          goal_code: code,
          handshake_protocols: [
            'https://didcomm.org/didexchange/1.0',
            'https://didcomm.org/connections/1.0',
          ],
          my_label: my_label.value,
          protocol_version: '1.1',
          use_public_did: false,
        })
      : await connectionStore.createInvitation(formFields.alias, multi.value);
    if (result != null && result['invitation_url']) {
      invitation_url.value = result['invitation_url'];
      console.log(`invitation_url: ${invitation_url.value}`);
      toast.info('Invitation Created');
      emit('success');
    }
    return false;
  } catch (error) {
    toast.error(`Failure: ${error}`);
  } finally {
    submitted.value = false;
  }
};
</script>

<style scoped lang="scss">
.settings-group {
  :deep(.p-panel-header) {
    border-radius: 0;
    border-top: none;
    border-left: none;
    border-right: none;
    background-color: transparent;
    padding-left: 0 !important;
  }
}
</style>
