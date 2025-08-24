import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { categoriesApi } from '../api/categories';
import type {
  Category,
  CategoryCreate,
  CategoryUpdate,
  CategoryListResponse,
} from '../types/category';

const CATEGORIES_QUERY_KEY = 'categories';
const CATEGORIES_HIERARCHY_QUERY_KEY = 'categories-hierarchy';
const REFETCH_INTERVAL = 5000; // 5 seconds

export const useCategories = (hierarchical?: boolean) => {
  return useQuery<CategoryListResponse, Error>({
    queryKey: [CATEGORIES_QUERY_KEY, { hierarchical }],
    queryFn: () => categoriesApi.getCategories(hierarchical),
    refetchInterval: REFETCH_INTERVAL,
    refetchIntervalInBackground: true,
    staleTime: 0,
  });
};

export const useCategoriesHierarchy = () => {
  return useQuery<Category[], Error>({
    queryKey: [CATEGORIES_HIERARCHY_QUERY_KEY],
    queryFn: () => categoriesApi.getCategoriesHierarchy(),
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
    onSuccess: (_newCategory) => {
      // Invalidate all category queries
      queryClient.invalidateQueries({ queryKey: [CATEGORIES_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: [CATEGORIES_HIERARCHY_QUERY_KEY] });
    },
  });
};

export const useUpdateCategory = () => {
  const queryClient = useQueryClient();

  return useMutation<Category, Error, { id: number; data: CategoryUpdate }>({
    mutationFn: ({ id, data }) => categoriesApi.updateCategory(id, data),
    onSuccess: (updatedCategory) => {
      // Update individual category cache
      queryClient.setQueryData([CATEGORIES_QUERY_KEY, updatedCategory.id], updatedCategory);
      // Invalidate all category queries since hierarchy might have changed
      queryClient.invalidateQueries({ queryKey: [CATEGORIES_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: [CATEGORIES_HIERARCHY_QUERY_KEY] });
    },
  });
};

export const useDeleteCategory = () => {
  const queryClient = useQueryClient();

  return useMutation<Category, Error, number>({
    mutationFn: categoriesApi.deleteCategory,
    onSuccess: (deletedCategory) => {
      // Remove individual category cache
      queryClient.removeQueries({ queryKey: [CATEGORIES_QUERY_KEY, deletedCategory.id] });
      // Invalidate all category queries since hierarchy might have changed
      queryClient.invalidateQueries({ queryKey: [CATEGORIES_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: [CATEGORIES_HIERARCHY_QUERY_KEY] });
    },
  });
};