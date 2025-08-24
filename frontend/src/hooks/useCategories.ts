import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { categoriesApi } from '../api/categories';
import type {
  Category,
  CategoryCreate,
  CategoryUpdate,
  CategoryListResponse,
} from '../types/category';

const CATEGORIES_QUERY_KEY = 'categories';
const REFETCH_INTERVAL = 5000; // 5 seconds

export const useCategories = () => {
  return useQuery<CategoryListResponse, Error>({
    queryKey: [CATEGORIES_QUERY_KEY],
    queryFn: () => categoriesApi.getCategories(),
    refetchInterval: REFETCH_INTERVAL,
    refetchIntervalInBackground: true,
    staleTime: 0,
  });
};

export const useCategory = (id: number | null) => {
  return useQuery<Category, Error>({
    queryKey: [CATEGORIES_QUERY_KEY, id],
    queryFn: () => categoriesApi.getCategory(id!),
    enabled: !!id,
    refetchInterval: REFETCH_INTERVAL,
    refetchIntervalInBackground: true,
  });
};

export const useCreateCategory = () => {
  const queryClient = useQueryClient();

  return useMutation<Category, Error, CategoryCreate>({
    mutationFn: categoriesApi.createCategory,
    onSuccess: (newCategory) => {
      // Optimistically update the cache
      queryClient.setQueryData<CategoryListResponse>(
        [CATEGORIES_QUERY_KEY],
        (oldData) => {
          if (!oldData) return oldData;
          return {
            ...oldData,
            items: [...oldData.items, newCategory],
            total: oldData.total + 1,
          };
        }
      );
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: [CATEGORIES_QUERY_KEY] });
    },
  });
};

export const useUpdateCategory = () => {
  const queryClient = useQueryClient();

  return useMutation<Category, Error, { id: number; data: CategoryUpdate }>({
    mutationFn: ({ id, data }) => categoriesApi.updateCategory(id, data),
    onSuccess: (updatedCategory) => {
      // Update cache
      queryClient.setQueryData<CategoryListResponse>(
        [CATEGORIES_QUERY_KEY],
        (oldData) => {
          if (!oldData) return oldData;
          return {
            ...oldData,
            items: oldData.items.map((category) =>
              category.id === updatedCategory.id ? updatedCategory : category
            ),
          };
        }
      );
      // Update individual category cache
      queryClient.setQueryData([CATEGORIES_QUERY_KEY, updatedCategory.id], updatedCategory);
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: [CATEGORIES_QUERY_KEY] });
    },
  });
};

export const useDeleteCategory = () => {
  const queryClient = useQueryClient();

  return useMutation<Category, Error, number>({
    mutationFn: categoriesApi.deleteCategory,
    onSuccess: (deletedCategory) => {
      // Remove from cache
      queryClient.setQueryData<CategoryListResponse>(
        [CATEGORIES_QUERY_KEY],
        (oldData) => {
          if (!oldData) return oldData;
          return {
            ...oldData,
            items: oldData.items.filter((category) => category.id !== deletedCategory.id),
            total: oldData.total - 1,
          };
        }
      );
      // Remove individual category cache
      queryClient.removeQueries({ queryKey: [CATEGORIES_QUERY_KEY, deletedCategory.id] });
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: [CATEGORIES_QUERY_KEY] });
    },
  });
};