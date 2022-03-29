import { lobService, sandboxService } from '@/services';
import { NotificationTypes } from '@/utils/constants';

// The store module to hold the "Alice" tenant components
export default {
  namespaced: true,
  state: {
    issuedCredentials: [],
    students: [],
    tenant: {}
  },
  getters: {
    issuedCredentials: state => state.issuedCredentials,
    students: state => state.students
      ? state.students.sort((a, b) => a.name.localeCompare(b.name))
      : [],
    tenant: state => state.tenant
  },
  mutations: {
    SET_ISSUED_CREDENTIALS(state, creds) {
      state.issuedCredentials = creds;
    },
    SET_STUDENTS(state, students) {
      state.students = students;
    },
    SET_TENANT(state, tenant) {
      state.tenant = tenant;
    }
  },
  actions: {
    // Query the showcase API the sandbox's set of students
    async getStudents({ commit, dispatch, rootState }) {
      try {
        const response = await sandboxService.getStudents(rootState.sandbox.currentSandbox.id);
        commit('SET_STUDENTS', response.data);
      }
      catch (error) {
        dispatch('notifications/addNotification', {
          message: 'An error occurred while fetching the Student list.',
          consoleError: `Error getting students: ${error}`,
        }, { root: true });
      }
    },
    // Inviter a student
    async inviteStudent({ dispatch, rootState, state }, student) {
      try {
        const response = await lobService.createInvitationStudent(
          rootState.sandbox.currentSandbox.id,
          state.tenant.id,
          student.id
        );
        if (response) {
          dispatch('notifications/addNotification', {
            message: `Invited ${student.name} to connect to Faber College.`,
            type: NotificationTypes.SUCCESS
          }, { root: true });
        }
      }
      catch (error) {
        dispatch('notifications/addNotification', {
          message: `An error while inviting ${student.name}.`,
          consoleError: `Error inviting: ${error}`,
        }, { root: true });
      }
    },
    // Issue a degree to a student
    async issueDegree({ dispatch, rootState, state }, student) {
      try {
        const response = lobService.issueDegree(
          rootState.sandbox.currentSandbox.id,
          state.tenant.id,
          student.id
        );
        if (response) {
          dispatch('notifications/addNotification', {
            message: `Issued a Degree Credential from ${state.tenant.name} to ${student.name}.`,
            type: NotificationTypes.SUCCESS
          }, { root: true });
        }
      }
      catch (error) {
        dispatch('notifications/addNotification', {
          message: `An error while issuing the degree to ${student.name}.`,
          consoleError: `Error issuing degree: ${error}`,
        }, { root: true });
      }
    },
    // Query the showcase API to fetch the Lobs issued credentials
    async getIssuedCredentials({ commit, dispatch, rootState, state }) {
      try {
        const response = await lobService.getIssuedCredentials(
          rootState.sandbox.currentSandbox.id,
          state.tenant.id);
        commit('SET_ISSUED_CREDENTIALS', response.data);
      }
      catch (error) {
        dispatch('notifications/addNotification', {
          message: 'An error occurred while fetching the Issued Credentials list.',
          consoleError: `Error getting issued credentials: ${error}`,
        }, { root: true });
      }
    },
    // Revoke a degree from a student
    async revokeDegree({ dispatch, rootState, state }, student) {
      try {
        const response = lobService.revokeDegree(
          rootState.sandbox.currentSandbox.id,
          state.tenant.id,
          student.id
        );
        if (response) {
          dispatch('notifications/addNotification', {
            message: `Revoking Degree Credential from ${student.name}.`,
            type: NotificationTypes.SUCCESS
          }, { root: true });
        }
      }
      catch (error) {
        dispatch('notifications/addNotification', {
          message: `An error while issuing the degree to ${student.name}.`,
          consoleError: `Error issuing degree: ${error}`,
        }, { root: true });
      }
    },

    // Re-get the relevant info for the Faber page
    async refreshLob({ dispatch }) {
      await dispatch('sandbox/refreshCurrentSandbox', {}, { root: true });
      await dispatch('getStudents');
      await dispatch('getIssuedCredentials');
    },
  }
};
