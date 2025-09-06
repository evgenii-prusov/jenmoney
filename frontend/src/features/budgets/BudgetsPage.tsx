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
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { useBudgets, useDeleteBudget } from '../../hooks/useBudgets';
import { categoriesApi } from '../../api/categories';
import { BudgetForm } from '../../components/BudgetForm';
import { ConfirmDialog } from '../../components/ConfirmDialog';
import { CategoryDisplay } from '../../components/CategoryDisplay';
import { createBudgetGroupSummaries } from '../../utils/budgetGrouping';
import type { Budget } from '../../types/budget';
import type { BudgetGroupSummary } from '../../utils/budgetGrouping';

export const BudgetsPage: React.FC = () => {
  const currentDate = new Date();
  const [selectedYear, setSelectedYear] = useState(currentDate.getFullYear());
  const [selectedMonth, setSelectedMonth] = useState(currentDate.getMonth() + 1);
  const [formOpen, setFormOpen] = useState(false);
  const [formMode, setFormMode] = useState<'create' | 'edit'>('create');
  const [selectedBudget, setSelectedBudget] = useState<Budget | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [budgetToDelete, setBudgetToDelete] = useState<Budget | null>(null);
  const [expandedGroups, setExpandedGroups] = useState<Set<number>>(new Set());

  // Queries - Use hierarchical categories to match Transactions page
  const { data: budgetsData, isLoading: budgetsLoading, error: budgetsError } = useBudgets(selectedYear, selectedMonth);
  const { data: categoriesResponse } = useQuery({
    queryKey: ['categories', 'hierarchical'],
    queryFn: () => categoriesApi.getCategories(true), // Use hierarchical categories
  });

  // Mutations
  const deleteMutation = useDeleteBudget();

  const budgets = budgetsData?.items || [];
  const summary = budgetsData?.summary;
  const categories = categoriesResponse?.items || [];

  // Separate budgets by type (income vs expense)
  const incomeBudgets = budgets.filter(budget => budget.category?.type === 'income');
  const expenseBudgets = budgets.filter(budget => budget.category?.type === 'expense');

  // Group budgets hierarchically within each type
  const incomeGroups = createBudgetGroupSummaries(incomeBudgets, categories);
  const expenseGroups = createBudgetGroupSummaries(expenseBudgets, categories);

  // Calculate summaries for each type
  const primaryCurrency = budgets.length > 0 ? budgets[0].currency : (summary?.currency || 'USD');
  const incomeSummary = {
    total_planned: incomeBudgets.reduce((sum, budget) => sum + parseFloat(budget.planned_amount), 0),
    total_actual: incomeBudgets.reduce((sum, budget) => sum + parseFloat(budget.actual_amount), 0),
    categories_count: incomeBudgets.length,
    currency: primaryCurrency
  };

  const expenseSummary = {
    total_planned: expenseBudgets.reduce((sum, budget) => sum + parseFloat(budget.planned_amount), 0),
    total_actual: expenseBudgets.reduce((sum, budget) => sum + parseFloat(budget.actual_amount), 0),
    categories_count: expenseBudgets.length,
    currency: primaryCurrency
  };

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

  const toggleGroupExpansion = (groupId: number) => {
    setExpandedGroups(prev => {
      const newSet = new Set(prev);
      if (newSet.has(groupId)) {
        newSet.delete(groupId);
      } else {
        newSet.add(groupId);
      }
      return newSet;
    });
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

  const renderGroupSummaryRow = (group: BudgetGroupSummary) => {
    const progressPercentage = getProgressPercentage(group.totalActual, group.totalPlanned);
    const remaining = getRemainingAmount(group.totalPlanned, group.totalActual);
    const progressColor = getProgressColor(progressPercentage);
    const isExpanded = expandedGroups.has(group.parentCategory.id);

    return (
      <TableRow 
        key={`group-${group.parentCategory.id}`}
        sx={{ 
          backgroundColor: 'action.hover',
          '&:hover': { backgroundColor: 'action.selected' }
        }}
      >
        <TableCell>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <IconButton
              size="small"
              onClick={() => toggleGroupExpansion(group.parentCategory.id)}
              sx={{ mr: 1 }}
            >
              {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
            <Box>
              <Typography variant="body1" fontWeight="bold" color="primary">
                {group.parentCategory.name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {group.children.length} subcategor{group.children.length === 1 ? 'y' : 'ies'}
              </Typography>
            </Box>
          </Box>
        </TableCell>
        <TableCell align="right">
          <Typography variant="body1" fontWeight="bold">
            {formatCurrency(group.totalPlanned, group.currency)}
          </Typography>
        </TableCell>
        <TableCell align="right">
          <Typography variant="body1" fontWeight="bold">
            {formatCurrency(group.totalActual, group.currency)}
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
            <Typography variant="body2" color="text.secondary" fontWeight="bold">
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
              fontWeight="bold"
            >
              {formatCurrency(Math.abs(remaining).toString(), group.currency)}
            </Typography>
          </Box>
        </TableCell>
        <TableCell align="right">
          <Typography variant="body2" color="text.secondary">
            Total
          </Typography>
        </TableCell>
      </TableRow>
    );
  };

  const renderBudgetRow = (budget: Budget, _budgetType: 'income' | 'expense', isChildBudget: boolean = false) => {
    const progressPercentage = getProgressPercentage(budget.actual_amount, budget.planned_amount);
    const remaining = getRemainingAmount(budget.planned_amount, budget.actual_amount);
    const progressColor = getProgressColor(progressPercentage);

    return (
      <TableRow 
        key={budget.id} 
        hover
        sx={isChildBudget ? { 
          backgroundColor: 'grey.50',
          '&:hover': { backgroundColor: 'grey.100' }
        } : undefined}
      >
        <TableCell sx={isChildBudget ? { pl: 6 } : undefined}>
          {budget.category ? (
            <CategoryDisplay 
              category={budget.category} 
              showDescription 
              showParentHierarchy={false} // Never show parent hierarchy for individual budgets in this view
              allCategories={categories}
            />
          ) : (
            <Typography variant="body1" fontWeight="medium">
              Category {budget.category_id}
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
  };

  const renderBudgetSection = (
    budgetGroups: { groupSummaries: BudgetGroupSummary[]; ungroupedBudgets: Budget[] }, 
    sectionType: 'income' | 'expense',
    sectionSummary: typeof incomeSummary
  ) => {
    const { groupSummaries, ungroupedBudgets } = budgetGroups;
    
    if (groupSummaries.length === 0 && ungroupedBudgets.length === 0) return null;

    const isIncome = sectionType === 'income';
    const sectionTitle = isIncome ? '📈 Income Budgets' : '💰 Expense Budgets';
    const sectionColor = isIncome ? 'success' : 'info';
    const actualColumnHeader = isIncome ? 'Actual Received' : 'Actual Spent';
    const remainingColumnHeader = isIncome ? 'Under/Over Budget' : 'Remaining';

    return (
      <Paper sx={{ mb: 3 }}>
        {/* Section Header */}
        <Box 
          sx={{ 
            p: 2, 
            backgroundColor: `${sectionColor}.main`,
            color: 'white',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}
        >
          <Typography variant="h6" fontWeight="bold">
            {sectionTitle}
          </Typography>
          <Stack direction="row" spacing={3}>
            <Box textAlign="center">
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                Total Planned: {formatCurrency(sectionSummary.total_planned.toString(), sectionSummary.currency)}
              </Typography>
            </Box>
            <Box textAlign="center">
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                Total Actual: {formatCurrency(sectionSummary.total_actual.toString(), sectionSummary.currency)}
              </Typography>
            </Box>
            <Box textAlign="center">
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                Categories: {sectionSummary.categories_count}
              </Typography>
            </Box>
          </Stack>
        </Box>

        {/* Section Table */}
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Category</TableCell>
                <TableCell align="right">Planned Amount</TableCell>
                <TableCell align="right">{actualColumnHeader}</TableCell>
                <TableCell align="center">Progress</TableCell>
                <TableCell align="right">{remainingColumnHeader}</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {/* Parent category groups */}
              {groupSummaries.map(group => {
                const isExpanded = expandedGroups.has(group.parentCategory.id);
                return (
                  <React.Fragment key={`group-${group.parentCategory.id}`}>
                    {renderGroupSummaryRow(group)}
                    {isExpanded && group.children.map(budget => 
                      renderBudgetRow(budget, sectionType, true)
                    )}
                  </React.Fragment>
                );
              })}
              
              {/* Top-level budgets (no parent) */}
              {ungroupedBudgets.map(budget => 
                renderBudgetRow(budget, sectionType, false)
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    );
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

      {/* Enhanced Summary Cards */}
      {summary && (
        <Paper sx={{ p: 3, mb: 3 }}>
          {/* Planned Row */}
          <Typography variant="h6" color="primary" gutterBottom>
            Planned Budget
          </Typography>
          <Stack direction="row" spacing={4} alignItems="center" sx={{ mb: 3 }}>
            <Box>
              <Typography variant="body1" color="success.main" fontWeight="medium">
                Planned Income
              </Typography>
              <Typography variant="h5" color="success.main">
                {formatCurrency(incomeSummary.total_planned.toString(), incomeSummary.currency)}
              </Typography>
            </Box>
            <Box>
              <Typography variant="body1" color="info.main" fontWeight="medium">
                Planned Expenses
              </Typography>
              <Typography variant="h5" color="info.main">
                {formatCurrency(expenseSummary.total_planned.toString(), expenseSummary.currency)}
              </Typography>
            </Box>
            <Box>
              <Typography variant="body1" color="text.secondary" fontWeight="medium">
                Planned Remaining
              </Typography>
              <Typography 
                variant="h5" 
                color={(incomeSummary.total_planned - expenseSummary.total_planned) >= 0 ? 'success.main' : 'error.main'}
              >
                {formatCurrency(
                  (incomeSummary.total_planned - expenseSummary.total_planned).toString(),
                  primaryCurrency
                )}
              </Typography>
            </Box>
          </Stack>

          {/* Actual Row */}
          <Typography variant="h6" color="text.secondary" gutterBottom>
            Actual Results
          </Typography>
          <Stack direction="row" spacing={4} alignItems="center">
            <Box>
              <Typography variant="body1" color="success.dark" fontWeight="medium">
                Actual Earnings
              </Typography>
              <Typography variant="h5" color="success.dark">
                {formatCurrency(incomeSummary.total_actual.toString(), incomeSummary.currency)}
              </Typography>
            </Box>
            <Box>
              <Typography variant="body1" color="info.dark" fontWeight="medium">
                Actual Expenses
              </Typography>
              <Typography variant="h5" color="info.dark">
                {formatCurrency(expenseSummary.total_actual.toString(), expenseSummary.currency)}
              </Typography>
            </Box>
            <Box>
              <Typography variant="body1" color="text.secondary" fontWeight="medium">
                Actual Difference
              </Typography>
              <Typography 
                variant="h5" 
                color={(incomeSummary.total_actual - expenseSummary.total_actual) >= 0 ? 'success.main' : 'error.main'}
              >
                {formatCurrency(
                  (incomeSummary.total_actual - expenseSummary.total_actual).toString(),
                  primaryCurrency
                )}
              </Typography>
            </Box>
          </Stack>
        </Paper>
      )}

      {/* Budgets Sections */}
      {budgetsLoading ? (
        <Paper>
          <Box sx={{ p: 3 }}>
            <Skeleton height={60} />
          </Box>
        </Paper>
      ) : budgets.length === 0 ? (
        <Paper>
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              No budgets found for {monthNames[selectedMonth - 1]} {selectedYear}
            </Typography>
          </Box>
        </Paper>
      ) : (
        <>
          {/* Income Budgets Section */}
          {renderBudgetSection(incomeGroups, 'income', incomeSummary)}
          
          {/* Expense Budgets Section */}
          {renderBudgetSection(expenseGroups, 'expense', expenseSummary)}
        </>
      )}

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