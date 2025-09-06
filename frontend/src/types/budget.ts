import type { Category } from './category';

export interface Budget {
  id: number;
  budget_year: number;
  budget_month: number;
  category_id: number;
  planned_amount: string;
  currency: string;
  created_at: string;
  updated_at: string;
  category?: Category;
  actual_amount: string;
}

export interface BudgetCreate {
  budget_year: number;
  budget_month: number;
  category_id: number;
  planned_amount: string;
  currency?: string; // Optional - will use user's default if not provided
}

export interface BudgetUpdate {
  planned_amount?: string;
  currency?: string;
}

export interface BudgetSummary {
  budget_year: number;
  budget_month: number;
  total_planned: string;
  total_actual: string;
  currency: string;
  categories_count: number;
  income_planned: string;
  income_actual: string;
  expense_planned: string;
  expense_actual: string;
}

export interface BudgetListResponse {
  items: Budget[];
  total: number;
  page: number;
  size: number;
  pages: number;
  summary?: BudgetSummary;
}