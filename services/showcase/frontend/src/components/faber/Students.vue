<template>
  <div class="students-list">
    <p>Add</p>
    <h2 class="my-4">Registered Student List</h2>
    <div v-if="currentSandbox">
      <!-- table header -->
      <v-data-table
        :headers="headers"
        item-key="id"
        :items="currentSandbox.students"
        disable-sort="true"
        disable-pagination
        hide-default-footer
      >
        <template #[`item.actions`]="{ item }">
          <!-- Invite user -->
          <v-tooltip bottom>
            <template #activator="{ on, attrs }">
              <v-btn
                @click="invite(item.id)"
                large
                icon
                v-bind="attrs"
                v-on="on"
              >
                <v-icon>person_add</v-icon>
              </v-btn>
            </template>
            <span>Send an Invitation</span>
          </v-tooltip>

          <!-- Issue Credential -->
          <v-tooltip bottom>
            <template #activator="{ on, attrs }">
              <v-btn
                @click="invite(item.id)"
                large
                icon
                v-bind="attrs"
                v-on="on"
              >
                <v-icon>generating_tokens</v-icon>
              </v-btn>
            </template>
            <span>Issue a Credential</span>
          </v-tooltip>

          <!-- View details -->
          <v-tooltip bottom>
            <template #activator="{ on, attrs }">
              <v-btn
                @click="invite(item.id)"
                large
                icon
                v-bind="attrs"
                v-on="on"
              >
                <v-icon>visibility</v-icon>
              </v-btn>
            </template>
            <span>View Student Details</span>
          </v-tooltip>
        </template>
      </v-data-table>
    </div>
    <div v-else>
      No sandbox session set, please go to Innkeeper tab to set that up
    </div>

    <v-skeleton-loader
      v-if="invitation || loadingInvitation"
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
        { text: 'Student', align: 'start', value: 'name' },
        {
          text: '',
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
        const faberTenant = this.currentSandbox.tenants.find(
          ({ name }) => name === 'Faber'
        );
        const response = await showcaseService.createInvitation(
          this.currentSandbox.id,
          faberTenant.id,
          id
        );
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

<style lang="scss">
.students-list {
  .v-data-table {
    table {
      border: 1px solid #173840;
    }
    padding: 0 5em;
    background-color: transparent !important;
    thead {
      background-color: #173840;
      tr th {
        color: white !important;
      }
      tr {
        border: 1px solid red !important;
      }
    }
  }
}
tbody {
  tr:hover {
    background-color: transparent !important;
  }
}
</style>

