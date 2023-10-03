import axios, { AxiosError } from 'axios';
import { useToast } from 'vue-toastification';

const toast = useToast();

const errorHandler = (
  error: any | AxiosError,
  existsMessage: string = 'The resource already exists'
) => {
  if (axios.isAxiosError(error))
    if (
      error.response?.data &&
      error.response?.data.includes('already exists')
    ) {
      toast.error(existsMessage);
      return;
    }

  toast.error(`Failure: ${error}`);
};

export default errorHandler;
