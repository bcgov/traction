<template>
  <div class="login">
    <div>
      <span class="p-float-label">
        <InputText v-model="key" type="text" autocomplete="username" name="username" autofocus />
        <label for="key">Wallet ID</label>
      </span>

      <span class="p-float-label">
        <InputText v-model="secret" type="password" autocomplete="current-password" name="password" />
        <label for="secret">Wallet Key</label>
      </span>
    </div>
    <div>
      <Button label="Clear" class="p-button-warning" @click="clear"></Button>
      <Button label="Submit" :disabled="!!loading" :loading="!!loading" @click="clicked"></Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';

// For notifications
import { useToast } from 'vue-toastification';
import { useTenantStore, useTokenStore } from '../store';
import { storeToRefs } from 'pinia';

const toast = useToast();

// To store credentials
const key = ref('');
const secret = ref('');

const tokenStore = useTokenStore();
// use the loading state from the store to disable the button...
const { loading, token } = storeToRefs(useTokenStore());
const tenantStore = useTenantStore();
const { tenant } = storeToRefs(useTenantStore());
/**
 * ##clicked
 * Read the form, formulate the request url then
 * request token from API
 */
const clicked = async () => {
  // the error is processed in the $onAction, add an empty handler to avoid Vue warning.
  try {
    await tokenStore.login(key.value, secret.value);
    console.log(token.value);
  } catch (err) {
      console.error(err);
      toast.error(`Failure getting token: ${err}`);
  }
  try {
    // token is loaded, now go fetch the tenant data...
    await tenantStore.getSelf();
    console.log(tenant.value);
  } catch (err) {
      console.error(err);
      toast.error(`Failure getting tenant: ${err}`);
  }

};

/**
 * ## clear
 * Clear the form
 */
const clear = () => {
  key.value = '';
  secret.value = '';
};
</script>

<style scoped>
span.p-float-label {
  margin: 25px;
}

button {
  margin: 0 20px;
}
</style>
