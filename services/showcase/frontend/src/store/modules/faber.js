import { sandboxService } from '@/services';

// The store module to hold the "Alice" tenant components
export default {
  namespaced: true,
  state: {
    students: [],
    tenant: {}
  },
  getters: {
    students: state => state.students
      ? state.students.sort((a, b) => a.name.localeCompare(b.name))
      : [],
    tenant: state => state.tenant
  },
  mutations: {
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
  }
};
