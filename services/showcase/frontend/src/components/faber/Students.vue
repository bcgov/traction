<template>
  <div>
    <h2>Students</h2>
    <div v-if="currentSandbox">
      <!-- table header -->
      <v-data-table
        :headers="headers"
        item-key="id"
        :items="currentSandbox.students"
      >
        <template #[`item.created_at`]="{ item }">
          {{ item.created_at | formatDateLong }}
        </template>
        <template #[`item.actions`]="{ item }">
          <v-btn color="primary" @click="invite(item.id)">Invite</v-btn>
        </template>
      </v-data-table>
    </div>
    <div v-else>
      No sandbox session set, please go to Innkeeper tab to set that up
    </div>

    <v-skeleton-loader
      v-if="invitation"
      :loading="loadingInvitation"
      type="card"
      max-width="600"
      class="mx-auto my-12"
    >
      <v-card class="mx-auto my-12" max-width="600" outlined>
        <v-card-title>Active Invitation</v-card-title>
        <v-card-text>
          {{ JSON.stringify(invitation, 0, 2) }}
        </v-card-text>
      </v-card>
    </v-skeleton-loader>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import { showcaseService } from '@/services';

export default {
  name: 'Students',
  data() {
    return {
      headers: [
        { text: 'name', align: 'start', value: 'name' },
        { text: 'Id', align: 'start', value: 'id' },
        { text: 'Created', align: 'start', value: 'created_at' },
        {
          text: 'Actions',
          align: 'end',
          value: 'actions',
          filterable: false,
          sortable: false,
        },
      ],
      invitation: null,
      loadingInvitation: false,
    };
  },
  computed: {
    ...mapGetters('sandbox', ['sandboxes', 'currentSandbox']),
  },
  methods: {
    async invite(id) {
      this.loadingInvitation = true;
      try {
        const response = await showcaseService.createSandbox(id);
        this.invitation = response.data;
      } catch (error) {
        alert('error creating invitation (TBD');
        this.invitation = { error: 'something bad' };
      } finally {
        this.loadingInvitation = false;
      }
    },
  },
};
</script>

<style>
</style>
