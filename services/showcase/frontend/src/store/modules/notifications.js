import { NotificationTypes } from '@/utils/constants';

// So each notification has a uniqueId in the session
let nextId = 1;

export default {
  namespaced: true,
  state: {
    notifications: []
  },
  getters: {
  },
  mutations: {
    PUSH(state, notification) {
      state.notifications.push({
        ...notification,
        id: nextId++
      });
    },
    DELETE(state, notificationToRemove) {
      state.notifications = state.notifications.filter(
        notification => notification.id !== notificationToRemove.id
      );
    },
    onNotification(state, notification) {
      //console.log('onNotification()');
      //console.log(notification);
      let msg = {
        message: `Notification from webhook for topic: ${notification.topic} for ${notification.lob.name}`,
        type: NotificationTypes.SUCCESS
      };
      state.notifications.push({
        ...msg,
        id: nextId++
      });
    }
  },
  actions: {
    addNotification({ commit }, notification) {
      if (notification.consoleError) console.error(notification.consoleError); // eslint-disable-line no-console
      if (!notification.type) notification = { ...notification, ...NotificationTypes.ERROR }; // Error (red) by default
      commit('PUSH', notification);
    },
    deleteNotification({ commit }, notificationToRemove) {
      commit('DELETE', notificationToRemove);
    }
  },
};
