<template>
  <div class="students-list">
    <v-row>
      <v-col cols="6">
        <div v-if="tenant.public_did">
          <v-icon color="success">check_circle_outline</v-icon> Faber University
          is an Issuer
        </div>
        <div v-else>
          <v-icon color="error">error_outline</v-icon> Faber University has not
          met the criteria to be an Issuer yet

          <v-tooltip bottom>
            <template #activator="{ on, attrs }">
              <v-btn
                large
                icon
                v-bind="attrs"
                v-on="on"
                @click="makeFaberIssuer()"
              >
                <v-icon>forward_to_inbox</v-icon>
              </v-btn>
            </template>
            <span>Request Issuer status</span>
          </v-tooltip>
        </div>
      </v-col>
      <v-col cols="6" class="text-right">
        <v-tooltip bottom>
          <template v-slot:activator="{ on, attrs }">
            <span v-bind="attrs" v-on="on">
              <v-icon>group</v-icon> office-admin-001
            </span>
          </template>
          <span>Not really logged in anywhere, just for show</span>
        </v-tooltip>
      </v-col>
    </v-row>
    <h2 class="my-4">Registered Student List</h2>
    <!-- table header -->
    <v-data-table
      :headers="headers"
      item-key="id"
      :items="students"
      disable-sort
      disable-pagination
      hide-default-footer
      :loading="loadingStudents"
    >
      <template #[`item.name`]="{ item }">
        {{ item.name }}
        <v-tooltip bottom v-if="item.wallet_id">
          <template v-slot:activator="{ on, attrs }">
            <span v-bind="attrs" v-on="on">
              <v-icon color="#173840">mdi-wallet</v-icon>
            </span>
          </template>
          <span>{{ item.name }} has a wallet registered in our system</span>
        </v-tooltip>
      </template>
      <template #[`item.actions`]="{ item }">
        <!-- Invite user -->
        <v-tooltip bottom>
          <template #activator="{ on, attrs }">
            <v-btn
              @click="invite(item.id)"
              :disabled="item.name != 'Alice Smith'"
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
              @click="issueDegree(item.id)"
              :disabled="!tenant.public_did"
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
              @click="showStudentDetails(item)"
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

    <!-- Dialog to show raw json -->
    <v-dialog v-model="studentDialog" width="800">
      <v-card>
        <v-card-title class="text-h5 grey lighten-2">
          Student Details
        </v-card-title>

        <v-card-text>
          <pre>{{ JSON.stringify(selectedStudent, 0, 2) }}</pre>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="studentDialog = false">
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';
import { lobService } from '@/services';

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
      loadingStudents: true,
      selectedStudent: {},
      studentDialog: false,
    };
  },
  computed: {
    ...mapGetters('faber', ['students', 'tenant']),
    ...mapGetters('sandbox', ['currentSandbox']),
  },
  methods: {
    ...mapActions('faber', ['getStudents']),
    ...mapActions('sandbox', ['makeIssuer']),
    async makeFaberIssuer() {
      await this.makeIssuer({
        tenantId: this.tenant.id,
        sandboxId: this.currentSandbox.id,
      });
    },
    showStudentDetails(student) {
      this.selectedStudent = student;
      this.studentDialog = true;
    },
    async invite(id) {
      this.loadingInvitation = true;
      try {
        const response = await lobService.createInvitationStudent(
          this.currentSandbox.id,
          this.tenant.id,
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
    async issueDegree(id) {
      this.loadingInvitation = true;
      try {
        const response = await lobService.issueDegree(
          this.currentSandbox.id,
          this.tenant.id,
          id
        );
        this.invitation = response.data;
      } catch (error) {
        alert('error issuing credential (TBD)');
        this.invitation = { error: 'something bad' };
      } finally {
        this.loadingInvitation = false;
      }
    },
  },
  async mounted() {
    await this.getStudents();
    this.loadingStudents = false;
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

