<template>
  <div class="grid w-screen h-screen">
    <div class="col-12 md:col-6 xl:col-4">
      <div class="px-8">
        <div class="pt-4 pb-6">
          <img src="/img/bc/bc_logo.png" class="logo-bc" />

          <img src="/img/logo/traction-logo-bc-text.svg" class="logo-traction" />
        </div>

        <div class="py-8">
          <LoginForm />
        </div>
      </div>
    </div>

    <div class="cover-image hidden md:block col-0 md:col-6 xl:col-8 p-0">
      <span v-if="config.ux.coverImageCopyright" class="copyright">
        {{ config.ux.coverImageCopyright }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';
import LoginForm from '@/components/LoginForm.vue';
import { useConfigStore } from '@/store';
const { config } = storeToRefs(useConfigStore());
</script>

<style scoped lang="scss">
.logo {
  display: block;
  margin-left: auto;
  margin-right: auto;
}
.logo-bc {
  @extend .logo;
  width: 18em;
}
.logo-traction {
  @extend .logo;
  width: 20em;
}

.cover-image {
  background-image: url('/img/default-login-image.jpg');
  background-repeat: no-repeat;
  background-size: cover;
  .copyright {
    color: white;
    font-size: 0.5em;
    background-color: rgba($color: #000000, $alpha: 0.5);
    padding: 0 0.5em;
    margin: 1em;
    position: absolute;
    bottom: 0;
    right: 0;
  }
}
</style>
