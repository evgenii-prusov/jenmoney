import { Currency } from './account';

export interface Transfer {
  id: number;
  from_account_id: number;
  to_account_id: number;
  from_amount: number;
  to_amount: number;
  from_currency: Currency;
  to_currency: Currency;
  exchange_rate?: number | null;
  description?: string | null;
  created_at: string;
  updated_at: string;
}

export interface TransferCreate {
  from_account_id: number;
  to_account_id: number;
  from_amount: number;
  to_amount?: number; // Optional for auto-calculation in same currency
  description?: string | null;
}

export interface TransferFormData {
  from_account_id: number;
  to_account_id: number;
  from_amount: number;
  to_amount: number;
  description: string;
}

export interface TransferValidationErrors {
  from_account_id?: string;
  to_account_id?: string;
  from_amount?: string;
  to_amount?: string;
  description?: string;
  general?: string;
}