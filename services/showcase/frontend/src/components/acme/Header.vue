<template>
  <v-toolbar dark flat prominent src="@/assets/images/computer.jpg">
    <template v-slot:img="{ props }">
      <v-img
        v-bind="props"
        gradient="to top right, rgba(42,80,82,.5), rgba(0,160,144,.8)"
      ></v-img>
    </template>
    <v-app-bar-nav-icon></v-app-bar-nav-icon>

    <v-toolbar-title>
      <v-icon x-large color="black">mdi-alpha-a-box</v-icon> ACME Corporation HR
      Portal
    </v-toolbar-title>

    <v-spacer></v-spacer>

    <v-btn icon @click="$emit('refresh')">
      <v-icon>mdi-refresh-auto</v-icon>
    </v-btn>
    <v-btn icon>
      <v-icon>mdi-key</v-icon>
    </v-btn>
    <v-btn icon>
      <v-icon>mdi-cube</v-icon>
    </v-btn>
    <v-btn icon>
      <v-icon>mdi-export</v-icon>
    </v-btn>
  </v-toolbar>
</template>

<script>
export default {
  name: 'AcmeHeader',
};
</script>
