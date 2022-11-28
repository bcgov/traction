import { PluginOptions, POSITION, TYPE } from 'vue-toastification';

const toastOptions: PluginOptions = {
  position: POSITION.BOTTOM_RIGHT,

  toastDefaults: {
    // ToastOptions object for each type of toast
    [TYPE.ERROR]: {
      icon: 'pi pi-times-circle',
    },
    [TYPE.SUCCESS]: {
      icon: 'pi pi-check-circle',
    },
    [TYPE.INFO]: {
      icon: 'pi pi-info-circle',
    },
    [TYPE.WARNING]: {
      icon: 'pi pi-exclamation-triangle',
    },
  },
};

export default toastOptions;
