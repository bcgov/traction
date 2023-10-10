import axios, { AxiosError } from 'axios';
import { useToast } from 'vue-toastification';

const toast = useToast();

const BAD_REQUEST_CODE = 'ERR_BAD_REQUEST';

interface ErrorHandler {
  error: any | AxiosError;
  existsMessage?: string;
  badRequestMessage?: string;
  internalMessage?: string;
}

const isDuplicate = (error: any | AxiosError) =>
  error.response?.data.includes('already exists') ||
  error.response?.data.includes('Duplicate row');

const errorHandler = ({
  error,
  existsMessage = 'Duplicate entry',
  badRequestMessage = 'Bad request',
  internalMessage = 'Internal server error',
}: ErrorHandler) => {
  if (axios.isAxiosError(error)) {
    if (error.response?.data && isDuplicate(error)) {
      toast.error(existsMessage);
      return;
    }
    if (error.code === BAD_REQUEST_CODE) {
      toast.error(badRequestMessage);
      return;
    }
  }

  toast.error(`Failure: ${internalMessage}`);
};

export default errorHandler;
