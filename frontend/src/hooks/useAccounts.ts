import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { accountsApi } from '../api/accounts';
import type {
  Account,
  AccountCreate,
  AccountUpdate,
  AccountListResponse,
  PaginationParams,
} from '../types/account';

const ACCOUNTS_QUERY_KEY = 'accounts';
const REFETCH_INTERVAL = 20000; // 20 seconds

export const useAccounts = (params?: PaginationParams) => {
  return useQuery<AccountListResponse, Error>({
    queryKey: [ACCOUNTS_QUERY_KEY, params],
    queryFn: () => accountsApi.getAccounts(params),
    refetchInterval: REFETCH_INTERVAL,
    refetchIntervalInBackground: true,
    staleTime: 0,
  });
};

export const useAccount = (id: number | null) => {
  return useQuery<Account, Error>({
    queryKey: [ACCOUNTS_QUERY_KEY, id],
    queryFn: () => accountsApi.getAccount(id!),
    enabled: !!id,
    refetchInterval: REFETCH_INTERVAL,
    refetchIntervalInBackground: true,
  });
};

export const useCreateAccount = () => {
  const queryClient = useQueryClient();

  return useMutation<Account, Error, AccountCreate>({
    mutationFn: accountsApi.createAccount,
    onSuccess: (newAccount) => {
      // Optimistically update the cache
      queryClient.setQueryData<AccountListResponse>(
        [ACCOUNTS_QUERY_KEY, undefined],
        (oldData) => {
          if (!oldData) return oldData;
          return {
            ...oldData,
            items: [...oldData.items, newAccount],
            total: oldData.total + 1,
          };
        }
      );
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: [ACCOUNTS_QUERY_KEY] });
    },
  });
};

export const useUpdateAccount = () => {
  const queryClient = useQueryClient();

  return useMutation<
    Account, 
    Error, 
    { id: number; data: AccountUpdate },
    { previousAccounts?: AccountListResponse }
  >({
    mutationFn: ({ id, data }) => accountsApi.updateAccount(id, data),
    onMutate: async ({ id, data }) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: [ACCOUNTS_QUERY_KEY] });

      // Snapshot the previous value
      const previousAccounts = queryClient.getQueryData<AccountListResponse>([
        ACCOUNTS_QUERY_KEY,
        undefined,
      ]);

      // Optimistically update the cache
      if (previousAccounts) {
        queryClient.setQueryData<AccountListResponse>(
          [ACCOUNTS_QUERY_KEY, undefined],
          {
            ...previousAccounts,
            items: previousAccounts.items.map((account) =>
              account.id === id ? { ...account, ...data } : account
            ),
          }
        );
      }

      // Return a context with the previous data
      return { previousAccounts };
    },
    onError: (_err, _variables, context) => {
      // If the mutation fails, use the context to rollback
      if (context?.previousAccounts) {
        queryClient.setQueryData(
          [ACCOUNTS_QUERY_KEY, undefined],
          context.previousAccounts
        );
      }
    },
    onSettled: () => {
      // Always refetch after error or success
      queryClient.invalidateQueries({ queryKey: [ACCOUNTS_QUERY_KEY] });
    },
  });
};

export const useDeleteAccount = () => {
  const queryClient = useQueryClient();

  return useMutation<
    Account, 
    Error, 
    number,
    { previousAccounts?: AccountListResponse }
  >({
    mutationFn: accountsApi.deleteAccount,
    onMutate: async (accountId) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: [ACCOUNTS_QUERY_KEY] });

      // Snapshot the previous value
      const previousAccounts = queryClient.getQueryData<AccountListResponse>([
        ACCOUNTS_QUERY_KEY,
        undefined,
      ]);

      // Optimistically update the cache
      if (previousAccounts) {
        queryClient.setQueryData<AccountListResponse>(
          [ACCOUNTS_QUERY_KEY, undefined],
          {
            ...previousAccounts,
            items: previousAccounts.items.filter(
              (account) => account.id !== accountId
            ),
            total: previousAccounts.total - 1,
          }
        );
      }

      // Return a context with the previous data
      return { previousAccounts };
    },
    onError: (_err, _variables, context) => {
      // If the mutation fails, use the context to rollback
      if (context?.previousAccounts) {
        queryClient.setQueryData(
          [ACCOUNTS_QUERY_KEY, undefined],
          context.previousAccounts
        );
      }
    },
    onSettled: () => {
      // Always refetch after error or success
      queryClient.invalidateQueries({ queryKey: [ACCOUNTS_QUERY_KEY] });
    },
  });
};