import React from 'react';
import { Box, Typography } from '@mui/material';
import { SubdirectoryArrowRight as SubdirectoryArrowRightIcon } from '@mui/icons-material';
import type { Category } from '../types/category';

interface CategoryDisplayProps {
  category: Category;
  showDescription?: boolean;
  variant?: 'inline' | 'stacked';
  showParentHierarchy?: boolean;
  allCategories?: Category[];
}

/**
 * Component to display a category with proper hierarchical indication
 * Shows parent category name with arrow if it's a child category
 */
export const CategoryDisplay: React.FC<CategoryDisplayProps> = ({
  category,
  showDescription = false,
  variant = 'stacked',
  showParentHierarchy = false,
  allCategories = [],
}) => {
  const isChildCategory = category.parent_id !== null && category.parent_id !== undefined;
  
  // Find parent category if hierarchy display is enabled
  const parentCategory = showParentHierarchy && isChildCategory && allCategories.length > 0
    ? findCategoryById(allCategories, category.parent_id!)
    : null;

  if (variant === 'inline') {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
        {showParentHierarchy && parentCategory ? (
          <>
            <Typography 
              variant="body2" 
              color="text.primary"
              fontWeight="medium"
            >
              {parentCategory.name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              &gt;
            </Typography>
            <Typography 
              variant="body2" 
              color="text.secondary"
            >
              {category.name}
            </Typography>
          </>
        ) : (
          <>
            {isChildCategory && (
              <SubdirectoryArrowRightIcon 
                sx={{ 
                  fontSize: '1rem',
                  color: 'action.active',
                }} 
              />
            )}
            <Typography 
              variant="body2" 
              color={isChildCategory ? 'text.secondary' : 'text.primary'}
              fontWeight={isChildCategory ? 'normal' : 'medium'}
            >
              {category.name}
            </Typography>
          </>
        )}
        {showDescription && category.description && (
          <Typography variant="body2" color="text.secondary">
            - {category.description}
          </Typography>
        )}
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
        {showParentHierarchy && parentCategory ? (
          <>
            <Typography 
              variant="body1" 
              color="text.primary"
              fontWeight="medium"
            >
              {parentCategory.name}
            </Typography>
            <Typography variant="body1" color="text.secondary">
              &gt;
            </Typography>
            <Typography 
              variant="body1" 
              color="text.secondary"
            >
              {category.name}
            </Typography>
          </>
        ) : (
          <>
            {isChildCategory && (
              <SubdirectoryArrowRightIcon 
                sx={{ 
                  fontSize: '1rem',
                  color: 'action.active',
                }} 
              />
            )}
            <Typography 
              variant="body1" 
              fontWeight={isChildCategory ? 'normal' : 'medium'}
              color={isChildCategory ? 'text.secondary' : 'text.primary'}
            >
              {category.name}
            </Typography>
          </>
        )}
      </Box>
      {showDescription && category.description && (
        <Typography variant="body2" color="text.secondary">
          {category.description}
        </Typography>
      )}
    </Box>
  );
};

/**
 * Helper function to find a category by ID from hierarchical category data
 * Searches both parent categories and their children
 */
export const findCategoryById = (categories: Category[], categoryId: number): Category | undefined => {
  for (const category of categories) {
    if (category.id === categoryId) {
      return category;
    }
    
    // Search in children
    if (category.children) {
      for (const child of category.children) {
        if (child.id === categoryId) {
          return child;
        }
      }
    }
  }
  
  return undefined;
};

/**
 * Helper function to create a flat map of all categories (including children)
 * from hierarchical category data for quick lookup
 */
export const createCategoryMap = (categories: Category[]): Record<number, Category> => {
  const categoryMap: Record<number, Category> = {};
  
  categories.forEach((category) => {
    categoryMap[category.id] = category;
    
    // Also add children to the map
    category.children?.forEach((child) => {
      categoryMap[child.id] = child;
    });
  });
  
  return categoryMap;
};