<template>
  <h3 class="mt-0">Tenant Profile</h3>

  <div class="grid">
    <div class="col-fixed w-30rem">
      <ProfileForm />
    </div>
    <div class="col text-right">
      <!-- Todo: badge -->
    </div>
  </div>
  <hr class="mb-4" />
  <ProfileFooter />
</template>

<script setup lang="ts">
import ProfileForm from '@/components/profile/ProfileForm.vue';
import ProfileFooter from '@/components/profile/ProfileFooter.vue';
</script>

<style scoped lang="scss">
hr {
  height: 1px;
  background-color: rgb(186, 186, 186);
  border: 0;
}
</style>
