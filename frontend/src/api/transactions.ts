import { apiClient } from './client';
import type { Transaction, TransactionCreate, TransactionUpdate } from '../types/transaction';

const TRANSACTIONS_ENDPOINT = '/transactions/';

export interface TransactionListResponse {
  items: Transaction[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface TransactionListParams {
  skip?: number;
  limit?: number;
  account_id?: number;
  category_id?: number;
}

export const transactionsApi = {
  createTransaction: async (transaction: TransactionCreate): Promise<Transaction> => {
    const { data } = await apiClient.post<Transaction>(TRANSACTIONS_ENDPOINT, transaction);
    return data;
  },

  getTransactions: async (params?: TransactionListParams): Promise<TransactionListResponse> => {
    const { data } = await apiClient.get<TransactionListResponse>(TRANSACTIONS_ENDPOINT, {
      params,
    });
    return data;
  },

  getTransaction: async (id: number): Promise<Transaction> => {
    const { data } = await apiClient.get<Transaction>(`${TRANSACTIONS_ENDPOINT}${id}`);
    return data;
  },

  updateTransaction: async (id: number, transaction: TransactionUpdate): Promise<Transaction> => {
    const { data } = await apiClient.patch<Transaction>(`${TRANSACTIONS_ENDPOINT}${id}`, transaction);
    return data;
  },

  deleteTransaction: async (id: number): Promise<Transaction> => {
    const { data } = await apiClient.delete<Transaction>(`${TRANSACTIONS_ENDPOINT}${id}`);
    return data;
  },
};

export default transactionsApi;