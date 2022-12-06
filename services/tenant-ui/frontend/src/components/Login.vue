<template>
  <div class="traction-login grid w-screen h-screen">
    <div class="col-12 md:col-6 xl:col-4">
      <div class="px-8">
        <div class="pt-4 pb-6">
          <img src="/img/bc/bc_logo.png" class="logo-bc" />

          <img
            src="/img/logo/traction-logo-bc-text.svg"
            class="logo-traction"
          />
        </div>

        <!-- Logging In -->
        <div v-if="loginMode === LOGIN_MODE.SIGNIN" class="py-6">
          <LoginForm />
          <div class="mt-6">
            <p>
              Don't have an account?
              <a
                href="#"
                class="p-button-link login-mode"
                @click.prevent="loginMode = LOGIN_MODE.RESERVE"
                >Create Request!</a
              >
            </p>
          </div>
        </div>

        <!-- Making Reservation -->
        <div v-else-if="loginMode === LOGIN_MODE.RESERVE" class="py-6">
          <Button
            label="Go Back to Sign-in"
            icon="pi pi-arrow-left"
            class="p-button-text"
            @click="loginMode = LOGIN_MODE.SIGNIN"
          />
          <Reserve />
        </div>
      </div>
    </div>

    <div class="cover-image hidden md:block col-0 md:col-6 xl:col-8 p-0">
      <span v-if="config.frontend.ux.coverImageCopyright" class="copyright">
        {{ config.frontend.ux.coverImageCopyright }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
// Vue
import { ref } from 'vue';
// PrimeVue
import Button from 'primevue/button';
// Components
import LoginForm from '@/components/LoginForm.vue';
import Reserve from './reservation/Reserve.vue';
// State
import { storeToRefs } from 'pinia';
import { useConfigStore } from '@/store';
const { config } = storeToRefs(useConfigStore());

// Other login form swtiching
enum LOGIN_MODE {
  SIGNIN,
  RESERVE,
  STATUS,
}
const loginMode = ref(LOGIN_MODE.SIGNIN);
const toggleLogin = () => {
  alert('hi');
};
</script>

<style scoped lang="scss">
// See layout.scss for generalized common login layout stuff
// Set the image specific to this component here though
.cover-image {
  background-image: url('/img/default-login-image.jpg');
}
</style>
