import { useMutation, useQueryClient } from '@tanstack/react-query';
import { transfersApi } from '../api/transfers';

export const useCreateTransfer = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: transfersApi.createTransfer,
    onSuccess: () => {
      // Invalidate accounts data to refresh balances after transfer
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
      queryClient.invalidateQueries({ queryKey: ['total-balance'] });
    },
  });
};