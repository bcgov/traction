<template>
  <Toolbar class="traction-header">
    <template #start>
      <i class="pi pi-bars p-toolbar-separator mr-2" />
    </template>

    <template #end>
      <select v-model="locale" class="mr-4">
        <option value="en">en</option>
        <option value="fr">fr</option>
      </select>

      <ProfileButton />
    </template>
  </Toolbar>
</template>

<script setup lang="ts">
import Toolbar from 'primevue/toolbar';
import ProfileButton from '@/components/profile/ProfileButton.vue';
import { useI18n } from 'vue-i18n';

const { locale } = useI18n({ useScope: 'global' });
</script>
