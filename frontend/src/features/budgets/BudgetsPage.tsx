import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  IconButton,
  Stack,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Fab,
  Alert,
  Skeleton,
  Tooltip,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  TrendingUp,
  TrendingDown,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { useBudgets, useDeleteBudget } from '../../hooks/useBudgets';
import { categoriesApi } from '../../api/categories';
import { BudgetForm } from '../../components/BudgetForm';
import { ConfirmDialog } from '../../components/ConfirmDialog';
import type { Budget } from '../../types/budget';

export const BudgetsPage: React.FC = () => {
  const currentDate = new Date();
  const [selectedYear, setSelectedYear] = useState(currentDate.getFullYear());
  const [selectedMonth, setSelectedMonth] = useState(currentDate.getMonth() + 1);
  const [formOpen, setFormOpen] = useState(false);
  const [formMode, setFormMode] = useState<'create' | 'edit'>('create');
  const [selectedBudget, setSelectedBudget] = useState<Budget | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [budgetToDelete, setBudgetToDelete] = useState<Budget | null>(null);

  // Queries
  const { data: budgetsData, isLoading: budgetsLoading, error: budgetsError } = useBudgets(selectedYear, selectedMonth);
  const { data: categoriesResponse } = useQuery({
    queryKey: ['categories'],
    queryFn: () => categoriesApi.getCategories(),
  });

  // Mutations
  const deleteMutation = useDeleteBudget();

  const budgets = budgetsData?.items || [];
  const summary = budgetsData?.summary;
  const categories = categoriesResponse?.items || [];

  // Month names for display
  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  // Year options (current year ±5)
  const yearOptions = Array.from({ length: 11 }, (_, i) => currentDate.getFullYear() - 5 + i);

  const handleCreateClick = () => {
    setFormMode('create');
    setSelectedBudget(null);
    setFormOpen(true);
  };

  const handleEditClick = (budget: Budget) => {
    setFormMode('edit');
    setSelectedBudget(budget);
    setFormOpen(true);
  };

  const handleDeleteClick = (budget: Budget) => {
    setBudgetToDelete(budget);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (budgetToDelete) {
      deleteMutation.mutate(budgetToDelete.id);
      setDeleteDialogOpen(false);
      setBudgetToDelete(null);
    }
  };

  const formatCurrency = (amount: string, currency: string = 'USD') => {
    const numAmount = parseFloat(amount);
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
    }).format(numAmount);
  };

  const getProgressPercentage = (actual: string, planned: string): number => {
    const actualNum = parseFloat(actual);
    const plannedNum = parseFloat(planned);
    if (plannedNum === 0) return 0;
    return Math.min((actualNum / plannedNum) * 100, 100);
  };

  const getProgressColor = (percentage: number): 'success' | 'warning' | 'error' => {
    if (percentage <= 75) return 'success';
    if (percentage <= 90) return 'warning';
    return 'error';
  };

  const getRemainingAmount = (planned: string, actual: string): number => {
    return parseFloat(planned) - parseFloat(actual);
  };

  if (budgetsError) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          Failed to load budgets. Please try again later.
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Budget Management
      </Typography>

      {/* Month/Year Selector */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Stack direction="row" spacing={2} alignItems="center">
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Month</InputLabel>
            <Select
              value={selectedMonth}
              label="Month"
              onChange={(e) => setSelectedMonth(e.target.value as number)}
            >
              {monthNames.map((month, index) => (
                <MenuItem key={index + 1} value={index + 1}>
                  {month}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Year</InputLabel>
            <Select
              value={selectedYear}
              label="Year"
              onChange={(e) => setSelectedYear(e.target.value as number)}
            >
              {yearOptions.map((year) => (
                <MenuItem key={year} value={year}>
                  {year}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Typography variant="h6" sx={{ ml: 2 }}>
            {monthNames[selectedMonth - 1]} {selectedYear}
          </Typography>
        </Stack>
      </Paper>

      {/* Summary Cards */}
      {summary && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Stack direction="row" spacing={4} alignItems="center">
            <Box>
              <Typography variant="h6" color="primary">
                Total Planned
              </Typography>
              <Typography variant="h4">
                {formatCurrency(summary.total_planned, summary.currency)}
              </Typography>
            </Box>
            <Box>
              <Typography variant="h6" color="text.secondary">
                Total Actual
              </Typography>
              <Typography variant="h4">
                {formatCurrency(summary.total_actual, summary.currency)}
              </Typography>
            </Box>
            <Box>
              <Typography variant="h6" color="text.secondary">
                Remaining
              </Typography>
              <Typography 
                variant="h4" 
                color={getRemainingAmount(summary.total_planned, summary.total_actual) >= 0 ? 'success.main' : 'error.main'}
              >
                {formatCurrency(
                  getRemainingAmount(summary.total_planned, summary.total_actual).toString(),
                  summary.currency
                )}
              </Typography>
            </Box>
            <Box>
              <Typography variant="h6" color="text.secondary">
                Categories
              </Typography>
              <Typography variant="h4">
                {summary.categories_count}
              </Typography>
            </Box>
          </Stack>
        </Paper>
      )}

      {/* Budgets Table */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Category</TableCell>
                <TableCell align="right">Planned Amount</TableCell>
                <TableCell align="right">Actual Spent</TableCell>
                <TableCell align="center">Progress</TableCell>
                <TableCell align="right">Remaining</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {budgetsLoading ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Skeleton height={60} />
                  </TableCell>
                </TableRow>
              ) : budgets.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Typography variant="body2" color="text.secondary">
                      No budgets found for {monthNames[selectedMonth - 1]} {selectedYear}
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                budgets.map((budget) => {
                  const progressPercentage = getProgressPercentage(budget.actual_amount, budget.planned_amount);
                  const remaining = getRemainingAmount(budget.planned_amount, budget.actual_amount);
                  const progressColor = getProgressColor(progressPercentage);

                  return (
                    <TableRow key={budget.id} hover>
                      <TableCell>
                        <Typography variant="body1" fontWeight="medium">
                          {budget.category?.name || `Category ${budget.category_id}`}
                        </Typography>
                        {budget.category?.description && (
                          <Typography variant="body2" color="text.secondary">
                            {budget.category.description}
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body1">
                          {formatCurrency(budget.planned_amount, budget.currency)}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body1">
                          {formatCurrency(budget.actual_amount, budget.currency)}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Box sx={{ minWidth: 120 }}>
                          <LinearProgress
                            variant="determinate"
                            value={progressPercentage}
                            color={progressColor}
                            sx={{ height: 8, borderRadius: 4, mb: 1 }}
                          />
                          <Typography variant="body2" color="text.secondary">
                            {progressPercentage.toFixed(1)}%
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                          {remaining >= 0 ? (
                            <TrendingUp color="success" fontSize="small" sx={{ mr: 0.5 }} />
                          ) : (
                            <TrendingDown color="error" fontSize="small" sx={{ mr: 0.5 }} />
                          )}
                          <Typography
                            variant="body1"
                            color={remaining >= 0 ? 'success.main' : 'error.main'}
                            fontWeight="medium"
                          >
                            {formatCurrency(Math.abs(remaining).toString(), budget.currency)}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <Tooltip title="Edit budget">
                          <IconButton
                            size="small"
                            onClick={() => handleEditClick(budget)}
                          >
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete budget">
                          <IconButton
                            size="small"
                            onClick={() => handleDeleteClick(budget)}
                            color="error"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Add Budget FAB */}
      <Fab
        color="primary"
        aria-label="add budget"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={handleCreateClick}
      >
        <AddIcon />
      </Fab>

      {/* Budget Form Dialog */}
      <BudgetForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        budget={selectedBudget}
        mode={formMode}
        defaultYear={selectedYear}
        defaultMonth={selectedMonth}
        categories={categories}
      />

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={deleteDialogOpen}
        onCancel={() => setDeleteDialogOpen(false)}
        onConfirm={handleDeleteConfirm}
        title="Delete Budget"
        message={
          budgetToDelete
            ? `Are you sure you want to delete the budget for "${budgetToDelete.category?.name || 'Unknown Category'}"? This action cannot be undone.`
            : ''
        }
        isDestructive={true}
      />
    </Box>
  );
};