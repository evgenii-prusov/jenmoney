export type CategoryType = 'income' | 'expense';

export interface Category {
  id: number;
  name: string;
  description?: string;
  type: CategoryType;
  parent_id?: number;
  created_at: string;
  updated_at: string;
  children?: Category[];
}

export interface CategoryCreate {
  name: string;
  description?: string;
  type: CategoryType;
  parent_id?: number;
}

export interface CategoryUpdate {
  name?: string;
  description?: string;
  type?: CategoryType;
  parent_id?: number;
}

export interface CategoryListResponse {
  items: Category[];
  total: number;
  page: number;
  size: number;
  pages: number;
}