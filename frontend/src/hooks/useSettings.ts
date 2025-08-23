import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { settingsApi } from '../api/settings';
import { Currency } from '../types/account';

// Define type locally to avoid Vite import issue
interface UserSettingsUpdate {
  default_currency?: Currency;
}

export const useSettings = () => {
  return useQuery({
    queryKey: ['settings'],
    queryFn: settingsApi.getSettings,
    refetchInterval: 5000,
  });
};

export const useUpdateSettings = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (settings: UserSettingsUpdate) => settingsApi.updateSettings(settings),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
      queryClient.invalidateQueries({ queryKey: ['totalBalance'] });
    },
  });
};

export const useTotalBalance = () => {
  return useQuery({
    queryKey: ['totalBalance'],
    queryFn: settingsApi.getTotalBalance,
    refetchInterval: 5000,
  });
};