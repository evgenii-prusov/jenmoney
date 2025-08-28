import React from 'react';
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import type { SelectChangeEvent } from '@mui/material/Select';
import { SubdirectoryArrowRight as SubdirectoryArrowRightIcon } from '@mui/icons-material';
import type { Category } from '../types/category';

interface CategorySelectorProps {
  categories: Category[];
  value: number | null | undefined;
  onChange: (value: number | null) => void;
  label?: string;
  helperText?: string;
  error?: boolean;
  required?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  size?: 'small' | 'medium';
  filterByType?: 'income' | 'expense';
  includeAllOption?: boolean;
  allOptionLabel?: string;
}

export const CategorySelector: React.FC<CategorySelectorProps> = ({
  categories,
  value,
  onChange,
  label = 'Category',
  helperText,
  error = false,
  required = false,
  disabled = false,
  fullWidth = true,
  size = 'medium',
  filterByType,
  includeAllOption = false,
  allOptionLabel = 'All Categories',
}) => {
  const handleChange = (event: SelectChangeEvent<string | number>) => {
    const selectedValue = event.target.value;
    if (selectedValue === '' || selectedValue === 'all') {
      onChange(null);
    } else {
      onChange(Number(selectedValue));
    }
  };

  // Helper function to render categories with hierarchy in dropdown
  const renderCategoryMenuItems = () => {
    const items: React.ReactNode[] = [];
    
    // Add "All Categories" option if requested
    if (includeAllOption) {
      items.push(
        <MenuItem key="all" value="all">
          {allOptionLabel}
        </MenuItem>
      );
    }

    // Add "No Category" option for non-required selectors
    if (!required) {
      items.push(
        <MenuItem key="none" value="">
          No Category
        </MenuItem>
      );
    }
    
    categories.forEach((category) => {
      // Add parent category if it matches type filter (or no filter)
      if (!filterByType || category.type === filterByType) {
        items.push(
          <MenuItem key={category.id} value={category.id}>
            {category.name}
          </MenuItem>
        );
      }
      
      // Add child categories with indentation if they match type filter (or no filter)
      category.children?.forEach((child) => {
        if (!filterByType || child.type === filterByType) {
          items.push(
            <MenuItem 
              key={child.id} 
              value={child.id}
              sx={{ 
                pl: 4,
                fontSize: '0.875rem',
                color: 'text.secondary',
                display: 'flex',
                alignItems: 'center',
                gap: 1,
              }}
            >
              <SubdirectoryArrowRightIcon 
                sx={{ 
                  fontSize: '1rem',
                  color: 'action.active',
                }} 
              />
              {child.name}
            </MenuItem>
          );
        }
      });
    });
    
    return items;
  };

  const displayValue = includeAllOption && value === null ? 'all' : (value || '');

  return (
    <FormControl 
      fullWidth={fullWidth} 
      error={error}
      size={size}
      disabled={disabled}
    >
      <InputLabel>{label}{required && ' *'}</InputLabel>
      <Select
        value={displayValue}
        label={`${label}${required ? ' *' : ''}`}
        onChange={handleChange}
      >
        {renderCategoryMenuItems()}
      </Select>
      {helperText && (
        <div style={{ fontSize: '0.75rem', color: error ? '#d32f2f' : '#666', marginTop: '3px', marginLeft: '14px' }}>
          {helperText}
        </div>
      )}
    </FormControl>
  );
};