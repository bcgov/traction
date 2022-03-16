<template>
  <v-container>
    <h1 class="my-6 text-center">Welcome</h1>
    <HelloWorld />
  </v-container>
</template>

<script>
import HelloWorld from '@/components/HelloWorld.vue';
export default {
  name: 'Home',
  components: {
    HelloWorld
  }
};
</script>
