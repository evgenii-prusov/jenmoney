import { apiClient } from './client';
import type {
  Category,
  CategoryCreate,
  CategoryUpdate,
  CategoryListResponse,
} from '../types/category';

const CATEGORIES_ENDPOINT = '/categories/';

export const categoriesApi = {
  getCategories: async (): Promise<CategoryListResponse> => {
    const { data } = await apiClient.get<CategoryListResponse>(CATEGORIES_ENDPOINT);
    return data;
  },

  getCategory: async (id: number): Promise<Category> => {
    const { data } = await apiClient.get<Category>(`${CATEGORIES_ENDPOINT}${id}`);
    return data;
  },

  createCategory: async (category: CategoryCreate): Promise<Category> => {
    const { data } = await apiClient.post<Category>(CATEGORIES_ENDPOINT, category);
    return data;
  },

  updateCategory: async (id: number, category: CategoryUpdate): Promise<Category> => {
    const { data } = await apiClient.patch<Category>(
      `${CATEGORIES_ENDPOINT}${id}`,
      category
    );
    return data;
  },

  deleteCategory: async (id: number): Promise<Category> => {
    const { data } = await apiClient.delete<Category>(`${CATEGORIES_ENDPOINT}${id}`);
    return data;
  },
};