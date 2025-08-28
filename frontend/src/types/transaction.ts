import { Currency } from './account';

export interface Transaction {
  id: number;
  account_id: number;
  amount: number;
  currency: Currency;
  category_id?: number | null;
  description?: string | null;
  transaction_date: string; // ISO date string
  created_at: string;
  updated_at: string;
}

export interface TransactionCreate {
  account_id: number;
  amount: number;
  category_id?: number | null;
  description?: string | null;
  transaction_date?: string; // ISO date string, defaults to today
}

export interface TransactionUpdate {
  amount?: number;
  category_id?: number | null;
  description?: string | null;
  transaction_date?: string; // ISO date string
}

export interface TransactionFormData {
  account_id: number;
  amount: number;
  category_id: number | null;
  description: string;
  transaction_date: string; // ISO date string
}

export interface TransactionValidationErrors {
  account_id?: string;
  amount?: string;
  category_id?: string;
  description?: string;
  transaction_date?: string;
  general?: string;
}