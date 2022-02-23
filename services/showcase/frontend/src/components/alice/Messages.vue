<template>
  <v-card>
    <v-card-title>
      <v-icon large left color="indigo"> mail </v-icon>
      <span class="text-h6">Messages</span>
    </v-card-title>

    <v-card-text>
      <v-skeleton-loader :loading="loading" type="list-item-two-line">
        <div v-if="ofbMessages">
          <ul>
            <li v-for="msg in ofbMessages" :key="msg.id" class="mb-4">
              <!-- Message Details -->
              <h3>{{ msg.msg_type }}</h3>
              {{ msg.created_at | formatDateLong }} <br />
              <strong>From:</strong> {{ msg.sender.name }}<br />
              <strong>To:</strong> {{ msg.recipient.name }} <br />

              <!-- Accept, reject -->
              <v-btn small color="primary" class="mr-4" @click="accept(msg)">
                Accept
              </v-btn>
              <v-btn small color="error" class="mr-4" @click="reject">
                Reject
              </v-btn>

              <!-- Dialog/btn to show raw json -->
              <v-dialog v-model="dialog" width="800">
                <template v-slot:activator="{ on, attrs }">
                  <v-btn small text v-bind="attrs" v-on="on"> Details </v-btn>
                </template>

                <v-card>
                  <v-card-title class="text-h5 grey lighten-2">
                    Out of Band Message Details
                  </v-card-title>

                  <v-card-text>
                    <pre>{{ JSON.stringify(msg, 0, 2) }}</pre>
                  </v-card-text>

                  <v-divider></v-divider>

                  <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="primary" text @click="dialog = false">
                      Close
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>
            </li>
          </ul>
        </div>
        <div v-else>
          <p>There are no messages to display</p>
        </div>
      </v-skeleton-loader>
    </v-card-text>
  </v-card>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'AliceMessages',
  data() {
    return {
      dialog: false,
      loading: true,
    };
  },
  computed: {
    ...mapGetters('alice', ['ofbMessages']),
  },
  methods: {
    ...mapActions('alice', ['accept', 'getOfbMessages']),
    reject() {
      alert('TBA');
    },
  },
  async mounted() {
    await this.getOfbMessages();
    this.loading = false;
  },
};
</script>

<style>
</style>
