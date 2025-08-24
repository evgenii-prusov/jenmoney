import { useSnackbar } from 'notistack';
import {
  useCategories,
  useCreateCategory,
  useUpdateCategory,
  useDeleteCategory,
} from './useCategories';
import type { CategoryCreate, CategoryUpdate } from '../types/category';

export const useCategoriesWithToast = (hierarchical?: boolean) => {
  return useCategories(hierarchical);
};

export const useCreateCategoryWithToast = () => {
  const { enqueueSnackbar } = useSnackbar();
  const mutation = useCreateCategory();

  const createCategory = async (data: CategoryCreate) => {
    try {
      const result = await mutation.mutateAsync(data);
      enqueueSnackbar('Category created successfully', { variant: 'success' });
      return result;
    } catch (error) {
      enqueueSnackbar('Failed to create category', { variant: 'error' });
      throw error;
    }
  };

  return {
    ...mutation,
    mutateAsync: createCategory,
  };
};

export const useUpdateCategoryWithToast = () => {
  const { enqueueSnackbar } = useSnackbar();
  const mutation = useUpdateCategory();

  const updateCategory = async (params: { id: number; data: CategoryUpdate }) => {
    try {
      const result = await mutation.mutateAsync(params);
      enqueueSnackbar('Category updated successfully', { variant: 'success' });
      return result;
    } catch (error) {
      enqueueSnackbar('Failed to update category', { variant: 'error' });
      throw error;
    }
  };

  return {
    ...mutation,
    mutateAsync: updateCategory,
  };
};

export const useDeleteCategoryWithToast = () => {
  const { enqueueSnackbar } = useSnackbar();
  const mutation = useDeleteCategory();

  const deleteCategory = async (id: number) => {
    try {
      const result = await mutation.mutateAsync(id);
      enqueueSnackbar('Category deleted successfully', { variant: 'success' });
      return result;
    } catch (error) {
      enqueueSnackbar('Failed to delete category', { variant: 'error' });
      throw error;
    }
  };

  return {
    ...mutation,
    mutateAsync: deleteCategory,
  };
};