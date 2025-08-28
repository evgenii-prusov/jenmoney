import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  MenuItem,
  Box,
  Alert,
  FormControl,
  InputLabel,
  Select,
} from '@mui/material';
import { useCreateBudget, useUpdateBudget } from '../hooks/useBudgets';
import type { Budget, BudgetCreate, BudgetUpdate } from '../types/budget';
import type { Category } from '../types/category';

interface BudgetFormProps {
  open: boolean;
  onClose: () => void;
  budget?: Budget | null;
  mode: 'create' | 'edit';
  defaultYear: number;
  defaultMonth: number;
  categories: Category[];
}

const currencies = [
  { value: 'USD', label: 'USD - US Dollar' },
  { value: 'EUR', label: 'EUR - Euro' },
  { value: 'RUB', label: 'RUB - Russian Ruble' },
  { value: 'JPY', label: 'JPY - Japanese Yen' },
];

const monthNames = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

export const BudgetForm: React.FC<BudgetFormProps> = ({
  open,
  onClose,
  budget,
  mode,
  defaultYear,
  defaultMonth,
  categories,
}) => {
  const [formData, setFormData] = useState({
    budget_year: defaultYear,
    budget_month: defaultMonth,
    category_id: 0,
    planned_amount: '',
    currency: 'USD',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const createMutation = useCreateBudget();
  const updateMutation = useUpdateBudget();

  const isSubmitting = createMutation.isPending || updateMutation.isPending;
  const submitError = createMutation.error?.message || updateMutation.error?.message;

  // Filter categories to only show expense categories
  const expenseCategories = categories.filter(cat => cat.type === 'expense');

  useEffect(() => {
    if (budget && mode === 'edit') {
      setFormData({
        budget_year: budget.budget_year,
        budget_month: budget.budget_month,
        category_id: budget.category_id,
        planned_amount: budget.planned_amount,
        currency: budget.currency,
      });
    } else {
      setFormData({
        budget_year: defaultYear,
        budget_month: defaultMonth,
        category_id: 0,
        planned_amount: '',
        currency: 'USD',
      });
    }
    setErrors({});
  }, [budget, mode, defaultYear, defaultMonth, open]);

  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.category_id) {
      newErrors.category_id = 'Category is required';
    }

    if (!formData.planned_amount || parseFloat(formData.planned_amount) <= 0) {
      newErrors.planned_amount = 'Planned amount must be greater than 0';
    }

    if (formData.budget_year < 2000 || formData.budget_year > 2100) {
      newErrors.budget_year = 'Year must be between 2000 and 2100';
    }

    if (formData.budget_month < 1 || formData.budget_month > 12) {
      newErrors.budget_month = 'Month must be between 1 and 12';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    try {
      if (mode === 'create') {
        const budgetCreate: BudgetCreate = {
          budget_year: formData.budget_year,
          budget_month: formData.budget_month,
          category_id: formData.category_id,
          planned_amount: formData.planned_amount,
          currency: formData.currency,
        };
        await createMutation.mutateAsync(budgetCreate);
      } else if (budget) {
        const budgetUpdate: BudgetUpdate = {
          planned_amount: formData.planned_amount,
          currency: formData.currency,
        };
        await updateMutation.mutateAsync({ id: budget.id, budget: budgetUpdate });
      }
      onClose();
    } catch (error) {
      // Error is handled by the mutation
    }
  };

  const yearOptions = Array.from({ length: 11 }, (_, i) => defaultYear - 5 + i);

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>
          {mode === 'create' ? 'Create Budget' : 'Edit Budget'}
        </DialogTitle>

        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            {submitError && (
              <Alert severity="error">
                {submitError}
              </Alert>
            )}

            {mode === 'create' && (
              <>
                <FormControl fullWidth error={!!errors.budget_year}>
                  <InputLabel>Year</InputLabel>
                  <Select
                    value={formData.budget_year}
                    label="Year"
                    onChange={(e) => handleChange('budget_year', e.target.value as number)}
                  >
                    {yearOptions.map((year) => (
                      <MenuItem key={year} value={year}>
                        {year}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <FormControl fullWidth error={!!errors.budget_month}>
                  <InputLabel>Month</InputLabel>
                  <Select
                    value={formData.budget_month}
                    label="Month"
                    onChange={(e) => handleChange('budget_month', e.target.value as number)}
                  >
                    {monthNames.map((month, index) => (
                      <MenuItem key={index + 1} value={index + 1}>
                        {month}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <FormControl fullWidth error={!!errors.category_id}>
                  <InputLabel>Category</InputLabel>
                  <Select
                    value={formData.category_id}
                    label="Category"
                    onChange={(e) => handleChange('category_id', e.target.value as number)}
                  >
                    <MenuItem value={0} disabled>
                      Select a category
                    </MenuItem>
                    {expenseCategories.map((category) => (
                      <MenuItem key={category.id} value={category.id}>
                        {category.name}
                        {category.description && ` - ${category.description}`}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </>
            )}

            {mode === 'edit' && budget && (
              <Box>
                <TextField
                  label="Period"
                  value={`${monthNames[budget.budget_month - 1]} ${budget.budget_year}`}
                  fullWidth
                  disabled
                  sx={{ mb: 2 }}
                />
                <TextField
                  label="Category"
                  value={budget.category?.name || `Category ${budget.category_id}`}
                  fullWidth
                  disabled
                />
              </Box>
            )}

            <TextField
              label="Planned Amount"
              type="number"
              value={formData.planned_amount}
              onChange={(e) => handleChange('planned_amount', e.target.value)}
              error={!!errors.planned_amount}
              helperText={errors.planned_amount}
              fullWidth
              required
              inputProps={{ step: '0.01', min: '0' }}
            />

            <TextField
              label="Currency"
              select
              value={formData.currency}
              onChange={(e) => handleChange('currency', e.target.value)}
              fullWidth
            >
              {currencies.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
          </Box>
        </DialogContent>

        <DialogActions>
          <Button onClick={onClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Saving...' : mode === 'create' ? 'Create' : 'Update'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};