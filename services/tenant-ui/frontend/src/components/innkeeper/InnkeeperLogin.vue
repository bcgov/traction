<template>
  <div class="grid w-screen h-screen">
    <div class="col-12 md:col-6 xl:col-4">
      <div class="px-8">
        <div class="pt-4 pb-6">Image and text UX TBD</div>

        <div class="py-8">
          <LoginForm />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import LoginForm from '@/components/innkeeper/InnkeeperLoginForm.vue';
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
</style>
