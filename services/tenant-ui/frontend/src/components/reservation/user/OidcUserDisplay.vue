<template>
  <div v-if="user">
    <strong>
      <i class="pi pi-user mr-2" />
      {{ user.profile?.name }} <a href="/">{{ $t('common.logout') }}</a>
    </strong>
  </div>
</template>

<script setup lang="ts">
// Vue
import { reactive, ref } from 'vue';
// State
import { useConfigStore, useOidcStore } from '@/store';
import { storeToRefs } from 'pinia';

const { config } = storeToRefs(useConfigStore());
const { user } = storeToRefs(useOidcStore());
</script>

<style scoped lang="scss">
a {
  border-left: 1px solid #000000;
  padding-left: 5px;
}
</style>
