<template>
  <v-alert
    :class="'target-notification ' + notification.class"
    :icon="notification.icon"
    prominent
    dismissible
    @input="alertClosed"
    transition="slide-y-transition"
  >
    {{ notification.message }}
  </v-alert>
</template>

<script>
import { mapActions } from 'vuex';
export default {
  name: 'BaseNotificationBar',
  props: {
    notification: {
      class: Object,
      icon: Object,
      message: Object,
    },
  },
  data() {
    return {
      timeout: null,
    };
  },
  methods: {
    ...mapActions('notifications', ['deleteNotification']),
    alertClosed() {
      this.deleteNotification(this.notification);
    },
  },
  mounted() {
    this.timeout = setTimeout(
      () => this.deleteNotification(this.notification),
      10000
    );
  },
  beforeDestroy() {
    // Prevent memory leak if component destroyed before timeout up
    clearTimeout(this.timeout);
  },
};
</script>

<style scoped>
  .target-notification >>> .v-alert__icon.v-icon:after {
    display: none;
  }
</style>
