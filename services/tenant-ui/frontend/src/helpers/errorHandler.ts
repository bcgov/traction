import axios, { AxiosError } from 'axios';
import { useToast } from 'vue-toastification';

const toast = useToast();

const isDuplicate = (error: any | AxiosError) =>
  error.response?.data.includes('already exists') ||
  error.response?.data.includes('Duplicate row');

const errorHandler = (
  error: any | AxiosError,
  existsMessage: string = 'The resource already exists'
) => {
  if (axios.isAxiosError(error))
    if (error.response?.data && isDuplicate(error)) {
      toast.error(existsMessage);
      return;
    }

  toast.error(`Failure: ${error}`);
};

export default errorHandler;
