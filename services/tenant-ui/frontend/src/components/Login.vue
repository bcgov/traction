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

        <div class="py-6">
          <LoginForm />
          <div class="mt-6">
            <p>
              Don't have an account?
              <a
                href="#"
                @click.prevent="toggleLogin()"
                class="p-button-link login-mode"
                >Create Request!</a
              >
            </p>
          </div>
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
// Components
import LoginForm from '@/components/LoginForm.vue';
// State
import { storeToRefs } from 'pinia';
import { useConfigStore } from '@/store';
const { config } = storeToRefs(useConfigStore());

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
