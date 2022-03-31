<template>
  <v-card>
    <v-card-title>
      <v-icon large left color="indigo"> mail </v-icon>
      <span class="text-h6">Messages</span>
    </v-card-title>

    <v-card-text>
      <v-skeleton-loader :loading="loading" type="list-item-two-line">
        <div v-if="ofbMessages && ofbMessages.length">
          <ul>
            <li v-for="msg in ofbMessages" :key="msg.id" class="mb-4">
              <!-- Message Details -->
              <div v-if="msg.msg_type === 'Invitation'">
                <h3>
                  {{ msg.msg_type }}
                  <small class="ml-3" v-if="msg.action === 'Accepted'">
                    <v-icon small color="success">check_circle </v-icon>
                    {{ msg.action }}
                  </small>
                  <small class="ml-3" v-else-if="msg.action === 'Rejected'">
                    <v-icon small color="error">cancel </v-icon>
                    {{ msg.action }}
                  </small>
                </h3>
                {{ msg.created_at | formatDateLong }} <br />
                <strong>From:</strong> {{ msg.sender.name }}<br />
                <strong>To:</strong> {{ msg.recipient.name }} <br />

                <!-- Accept, reject -->
                <v-btn
                  v-if="!msg.action"
                  small
                  color="primary"
                  class="white--text mr-4"
                  @click="accept(msg)"
                >
                  Accept
                </v-btn>
                <v-btn
                  v-if="!msg.action"
                  small
                  color="error"
                  class="white--text mr-4"
                  @click="reject(msg)"
                >
                  Reject
                </v-btn>

                <v-btn small outlined @click="showRawMsg(msg)"> Details </v-btn>
              </div>
              <div v-if="msg.msg_type === 'Revocation'">
                <h3>
                  {{ msg.msg_type }}
                  <small class="ml-3">
                    <v-icon small color="error">cancel</v-icon>
                  </small>
                </h3>
                {{ msg.created_at | formatDateLong }} <br />
                {{ msg.msg.comment }} <br />
                <v-btn small outlined @click="showRawMsg(msg)"> Details </v-btn>
              </div>
            </li>
          </ul>
        </div>
        <div v-else>
          <p>There are no messages to display</p>
        </div>
      </v-skeleton-loader>
    </v-card-text>

    <!-- Dialog/btn to show raw json -->
    <v-dialog v-model="dialog" width="1000">
      <v-card>
        <v-card-title class="text-h5 grey lighten-2">
          Out of Band Message Details
        </v-card-title>

        <v-card-text>
          <pre>{{ JSON.stringify(rawMsgToShow, 0, 2) }}</pre>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="dialog = false"> Close </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
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
      rawMsgToShow: {},
    };
  },
  computed: {
    ...mapGetters('alice', ['ofbMessages']),
  },
  methods: {
    ...mapActions('alice', ['accept', 'reject', 'getOfbMessages']),
    showRawMsg(msg) {
      this.rawMsgToShow = msg;
      this.dialog = true;
    }
  },
  async mounted() {
    await this.getOfbMessages();
    this.loading = false;
  },
};
</script>

<style>
</style>
