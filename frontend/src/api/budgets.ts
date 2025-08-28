import { apiClient } from './client';
import type {
  Budget,
  BudgetCreate,
  BudgetUpdate,
  BudgetListResponse,
} from '../types/budget';

const BUDGETS_ENDPOINT = '/budgets/';

export const budgetsApi = {
  getBudgets: async (params: {
    year: number;
    month: number;
    skip?: number;
    limit?: number;
  }): Promise<BudgetListResponse> => {
    const { data } = await apiClient.get<BudgetListResponse>(BUDGETS_ENDPOINT, { params });
    return data;
  },

  getBudget: async (id: number): Promise<Budget> => {
    const { data } = await apiClient.get<Budget>(`${BUDGETS_ENDPOINT}${id}`);
    return data;
  },

  createBudget: async (budget: BudgetCreate): Promise<Budget> => {
    const { data } = await apiClient.post<Budget>(BUDGETS_ENDPOINT, budget);
    return data;
  },

  updateBudget: async (id: number, budget: BudgetUpdate): Promise<Budget> => {
    const { data } = await apiClient.patch<Budget>(
      `${BUDGETS_ENDPOINT}${id}`,
      budget
    );
    return data;
  },

  deleteBudget: async (id: number): Promise<Budget> => {
    const { data } = await apiClient.delete<Budget>(`${BUDGETS_ENDPOINT}${id}`);
    return data;
  },
};