import { apiClient } from './client';
import type {
  Account,
  AccountCreate,
  AccountUpdate,
  AccountListResponse,
  PaginationParams,
} from '../types/account';

const ACCOUNTS_ENDPOINT = '/accounts';

export const accountsApi = {
  getAccounts: async (params?: PaginationParams): Promise<AccountListResponse> => {
    const { data } = await apiClient.get<AccountListResponse>(ACCOUNTS_ENDPOINT, {
      params,
    });
    return data;
  },

  getAccount: async (id: number): Promise<Account> => {
    const { data } = await apiClient.get<Account>(`${ACCOUNTS_ENDPOINT}/${id}`);
    return data;
  },

  createAccount: async (account: AccountCreate): Promise<Account> => {
    const { data } = await apiClient.post<Account>(ACCOUNTS_ENDPOINT, account);
    return data;
  },

  updateAccount: async (id: number, account: AccountUpdate): Promise<Account> => {
    const { data } = await apiClient.patch<Account>(
      `${ACCOUNTS_ENDPOINT}/${id}`,
      account
    );
    return data;
  },

  deleteAccount: async (id: number): Promise<Account> => {
    const { data } = await apiClient.delete<Account>(`${ACCOUNTS_ENDPOINT}/${id}`);
    return data;
  },
};

export default accountsApi;