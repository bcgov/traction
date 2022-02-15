<template>
  <v-container>
    <h1 class="my-6 text-center">Faber</h1>
    <Students />
  </v-container>
</template>

<script>
import Students from '@/components/faber/Students.vue';
export default {
  name: 'Faber',
  components: {
    Students
  }
};
</script>
