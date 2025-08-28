import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { budgetsApi } from '../api/budgets';
import type { BudgetCreate, BudgetUpdate } from '../types/budget';

// Query for budgets list
export function useBudgets(year: number, month: number) {
  return useQuery({
    queryKey: ['budgets', year, month],
    queryFn: () => budgetsApi.getBudgets({ year, month }),
    refetchInterval: 5000, // Auto-refresh every 5 seconds
  });
}

// Query for single budget
export function useBudget(id: number) {
  return useQuery({
    queryKey: ['budget', id],
    queryFn: () => budgetsApi.getBudget(id),
    enabled: !!id,
  });
}

// Mutation for creating budget
export function useCreateBudget() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (budget: BudgetCreate) => budgetsApi.createBudget(budget),
    onSuccess: (newBudget) => {
      // Invalidate budgets list for the specific month
      queryClient.invalidateQueries({
        queryKey: ['budgets', newBudget.budget_year, newBudget.budget_month],
      });
    },
  });
}

// Mutation for updating budget
export function useUpdateBudget() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, budget }: { id: number; budget: BudgetUpdate }) =>
      budgetsApi.updateBudget(id, budget),
    onSuccess: (updatedBudget) => {
      // Update the specific budget in cache
      queryClient.setQueryData(['budget', updatedBudget.id], updatedBudget);
      
      // Invalidate budgets list for the specific month
      queryClient.invalidateQueries({
        queryKey: ['budgets', updatedBudget.budget_year, updatedBudget.budget_month],
      });
    },
  });
}

// Mutation for deleting budget
export function useDeleteBudget() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => budgetsApi.deleteBudget(id),
    onSuccess: (deletedBudget) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: ['budget', deletedBudget.id] });
      
      // Invalidate budgets list for the specific month
      queryClient.invalidateQueries({
        queryKey: ['budgets', deletedBudget.budget_year, deletedBudget.budget_month],
      });
    },
  });
}