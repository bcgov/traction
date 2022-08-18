<script setup lang="ts">
import { ref } from 'vue';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';

// For notifications
import { useToast } from 'vue-toastification';
import { useTokenStore } from '../store/tokenStore';
import { storeToRefs } from 'pinia';
const toast = useToast();

// To store credentials
const key = ref('');
const secret = ref('');

const tokenStore = useTokenStore();

tokenStore.$onAction(({ name, after, onError }) => {
  if (name == 'load') {
    // this is after a successful load of the token...
    after((result) => {
      console.log(`Access Token: ${result}`);
    });

    // and this called if load throws an error
    onError((err) => {
      console.error(err);
      toast.error(`Failure: ${err}`);
    });
  }
});

// use the loading state from the store to disable the button...
const { loading } = storeToRefs(useTokenStore());

/**
 * ##clicked
 * Read the form, formulate the request url then
 * request token from API
 */
const clicked = async () => {
  // the error is processed in the $onAction, add an empty handler to avoid Vue warning.
  await tokenStore.load(key.value, secret.value).catch(() => {});
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

<style scoped>
span.p-float-label {
  margin: 25px;
}

button {
  margin: 0 20px;
}
</style>
