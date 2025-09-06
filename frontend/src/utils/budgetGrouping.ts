import type { Budget } from '../types/budget';
import type { Category } from '../types/category';

export interface BudgetGroupSummary {
  parentCategory: Category;
  totalPlanned: string;
  totalActual: string;
  currency: string;
  children: Budget[];
}

/**
 * Groups budgets by parent category for hierarchical display
 */
export function createBudgetGroupSummaries(
  budgets: Budget[],
  categories: Category[]
): { groupSummaries: BudgetGroupSummary[]; ungroupedBudgets: Budget[] } {
  // Create a map of all categories for easy lookup
  const categoryMap = new Map<number, Category>();
  categories.forEach(cat => {
    categoryMap.set(cat.id, cat);
    cat.children?.forEach(child => {
      categoryMap.set(child.id, child);
    });
  });

  // Group budgets by parent category
  const parentGroups = new Map<number, BudgetGroupSummary>();
  const ungroupedBudgets: Budget[] = [];

  budgets.forEach(budget => {
    if (!budget.category) {
      ungroupedBudgets.push(budget);
      return;
    }

    const category = budget.category;
    
    if (category.parent_id) {
      // This is a child category budget
      const parentId = category.parent_id;
      const parentCategory = categoryMap.get(parentId);
      
      if (parentCategory) {
        if (!parentGroups.has(parentId)) {
          parentGroups.set(parentId, {
            parentCategory,
            totalPlanned: '0',
            totalActual: '0',
            currency: budget.currency,
            children: [],
          });
        }
        
        const group = parentGroups.get(parentId)!;
        group.children.push(budget);
        
        // Update totals
        group.totalPlanned = (
          parseFloat(group.totalPlanned) + parseFloat(budget.planned_amount)
        ).toFixed(2);
        group.totalActual = (
          parseFloat(group.totalActual) + parseFloat(budget.actual_amount)
        ).toFixed(2);
      }
    } else {
      // This is a top-level category budget
      ungroupedBudgets.push(budget);
    }
  });

  const groupSummaries = Array.from(parentGroups.values())
    .sort((a, b) => a.parentCategory.name.localeCompare(b.parentCategory.name));

  return { groupSummaries, ungroupedBudgets };
}