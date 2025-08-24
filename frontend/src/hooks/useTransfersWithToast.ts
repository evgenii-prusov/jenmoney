import { useSnackbar } from 'notistack';
import { useCreateTransfer } from './useTransfers';
import type { TransferCreate } from '../types/transfer';

export const useCreateTransferWithToast = () => {
  const { enqueueSnackbar } = useSnackbar();
  const mutation = useCreateTransfer();

  const createTransfer = async (data: TransferCreate) => {
    try {
      const result = await mutation.mutateAsync(data);
      enqueueSnackbar('Transfer completed successfully', { variant: 'success' });
      return result;
    } catch (error) {
      enqueueSnackbar('Failed to complete transfer', { variant: 'error' });
      throw error;
    }
  };

  return {
    ...mutation,
    mutateAsync: createTransfer,
  };
};