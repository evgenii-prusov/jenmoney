import { useSnackbar } from 'notistack';
import {
  useAccounts,
  useCreateAccount,
  useUpdateAccount,
  useDeleteAccount,
} from './useAccounts';
import type { AccountCreate, AccountUpdate } from '../types/account';

export const useAccountsWithToast = () => {
  return useAccounts();
};

export const useCreateAccountWithToast = () => {
  const { enqueueSnackbar } = useSnackbar();
  const mutation = useCreateAccount();

  const createAccount = async (data: AccountCreate) => {
    try {
      const result = await mutation.mutateAsync(data);
      enqueueSnackbar('Account created successfully', { variant: 'success' });
      return result;
    } catch (error) {
      enqueueSnackbar('Failed to create account', { variant: 'error' });
      throw error;
    }
  };

  return {
    ...mutation,
    mutateAsync: createAccount,
  };
};

export const useUpdateAccountWithToast = () => {
  const { enqueueSnackbar } = useSnackbar();
  const mutation = useUpdateAccount();

  const updateAccount = async (params: { id: number; data: AccountUpdate }) => {
    try {
      const result = await mutation.mutateAsync(params);
      enqueueSnackbar('Account updated successfully', { variant: 'success' });
      return result;
    } catch (error) {
      enqueueSnackbar('Failed to update account', { variant: 'error' });
      throw error;
    }
  };

  return {
    ...mutation,
    mutateAsync: updateAccount,
  };
};

export const useDeleteAccountWithToast = () => {
  const { enqueueSnackbar } = useSnackbar();
  const mutation = useDeleteAccount();

  const deleteAccount = async (id: number) => {
    try {
      const result = await mutation.mutateAsync(id);
      enqueueSnackbar('Account deleted successfully', { variant: 'success' });
      return result;
    } catch (error) {
      enqueueSnackbar('Failed to delete account', { variant: 'error' });
      throw error;
    }
  };

  return {
    ...mutation,
    mutateAsync: deleteAccount,
  };
};