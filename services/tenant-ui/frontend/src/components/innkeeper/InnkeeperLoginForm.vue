<template>
  <form @submit.prevent="handleSubmit(!v$.$invalid)">
    <div class="field mt-5 w-full">
      <!-- ID -->
      <label
        for="admin-name"
        :class="{ 'p-error': v$.adminName.$invalid && submitted }"
      >
        {{ $t('admin.adminName') }}
      </label>
      <InputText
        id="admin-name"
        v-model="v$.adminName.$model"
        type="text"
        option-label="label"
        autocomplete="username"
        autofocus
        class="w-full"
      />
      <small v-if="v$.adminName.$invalid && submitted" class="p-error">{{
        v$.adminName.required.$message
      }}</small>
    </div>

    <div class="field mt-5 w-full">
      <!-- Secret -->
      <label
        for="admin-key"
        :class="{ 'p-error': v$.adminKey.$invalid && submitted }"
      >
        {{ $t('admin.adminKey') }}
      </label>
      <InputText
        id="admin-key"
        v-model="v$.adminKey.$model"
        type="password"
        autocomplete="current-password"
        class="w-full"
      />
      <small v-if="v$.adminKey.$invalid && submitted" class="p-error">{{
        v$.adminKey.required.$message
      }}</small>

      <Button
        type="submit"
        class="w-full mt-5"
        label="Sign-In"
        :disabled="!!loading"
        :loading="!!loading"
      />
    </div>
  </form>
</template>

<script setup lang="ts">
//Vue
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
// PrimeVue/Validation/etc
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import { useToast } from 'vue-toastification';
import { required } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
// State
import { useInnkeeperTokenStore } from '@/store';
import { storeToRefs } from 'pinia';

const toast = useToast();
const router = useRouter();

// Login Form and validation
const formFields = reactive({
  adminName: '',
  adminKey: '',
});
const rules = {
  adminName: { required },
  adminKey: { required },
};
const v$ = useVuelidate(rules, formFields);

// State setup
const innkeeperTokenStore = useInnkeeperTokenStore();
// use the loading state from the store to disable the button...
const { loading } = storeToRefs(useInnkeeperTokenStore());

// Form submission
const submitted = ref(false);
const handleSubmit = async (isFormValid: boolean): Promise<void> => {
  submitted.value = true;

  if (!isFormValid) {
    return;
  }
  try {
    await innkeeperTokenStore.login(formFields);
    router.push({ name: 'InnkeeperTenants' });
  } catch (err) {
    console.error(err);
    toast.error(`Failure getting token: ${err}`);
  }
};
</script>
