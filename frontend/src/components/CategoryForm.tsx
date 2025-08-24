import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
} from '@mui/material';
import type { Category, CategoryCreate, CategoryUpdate, CategoryType } from '../types/category';

interface CategoryFormProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: CategoryCreate | CategoryUpdate) => Promise<void>;
  category?: Category | null;
  mode: 'create' | 'edit';
  availableCategories?: Category[];
}

export const CategoryForm: React.FC<CategoryFormProps> = ({
  open,
  onClose,
  onSubmit,
  category,
  mode,
  availableCategories = [],
}) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    type: 'expense' as CategoryType,
    parent_id: undefined as number | undefined,
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Get only parent categories of the same type for selection
  const parentCategories = availableCategories.filter(cat => 
    !cat.parent_id && 
    (!category || cat.id !== category.id) &&
    cat.type === formData.type
  );

  useEffect(() => {
    if (category && mode === 'edit') {
      setFormData({
        name: category.name,
        description: category.description || '',
        type: category.type,
        parent_id: category.parent_id,
      });
    } else if (mode === 'create') {
      setFormData({
        name: '',
        description: '',
        type: 'expense',
        parent_id: undefined,
      });
    }
    setErrors({});
    setSubmitError(null);
  }, [category, mode, open]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Category name is required';
    } else if (formData.name.length > 100) {
      newErrors.name = 'Category name must be 100 characters or less';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      const submitData = {
        name: formData.name.trim(),
        description: formData.description.trim() || undefined,
        type: formData.type,
        parent_id: formData.parent_id || undefined,
      };

      await onSubmit(submitData);
      onClose();
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : 'An unexpected error occurred');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (field: keyof typeof formData) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData(prev => ({
      ...prev,
      [field]: e.target.value,
    }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: '',
      }));
    }
  };

  const handleTypeChange = (value: CategoryType) => {
    setFormData(prev => ({
      ...prev,
      type: value,
      // Reset parent when changing type since parent must be same type
      parent_id: undefined,
    }));
  };

  const handleParentChange = (value: number | '') => {
    setFormData(prev => ({
      ...prev,
      parent_id: value === '' ? undefined : value,
    }));
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="sm" 
      fullWidth
      PaperProps={{
        sx: { borderRadius: 2 }
      }}
    >
      <form onSubmit={handleSubmit}>
        <DialogTitle sx={{ pb: 1 }}>
          {mode === 'create' ? 'Create Category' : 'Edit Category'}
        </DialogTitle>
        
        <DialogContent sx={{ py: 2 }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            {submitError && (
              <Alert severity="error" sx={{ mt: 0 }}>
                {submitError}
              </Alert>
            )}

            <TextField
              label="Category Name"
              value={formData.name}
              onChange={handleInputChange('name')}
              error={!!errors.name}
              helperText={errors.name}
              required
              fullWidth
              disabled={isSubmitting}
              sx={{ mt: 1 }}
            />

            <FormControl fullWidth disabled={isSubmitting}>
              <InputLabel>Category Type</InputLabel>
              <Select
                value={formData.type}
                onChange={(e) => handleTypeChange(e.target.value as CategoryType)}
                label="Category Type"
                required
              >
                <MenuItem value="income">Income</MenuItem>
                <MenuItem value="expense">Expense</MenuItem>
              </Select>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, px: 1 }}>
                Income categories track money coming in, expense categories track money going out.
              </Typography>
            </FormControl>

            <FormControl fullWidth disabled={isSubmitting}>
              <InputLabel>Parent Category (Optional)</InputLabel>
              <Select
                value={formData.parent_id || ''}
                onChange={(e) => handleParentChange(e.target.value as number | '')}
                label="Parent Category (Optional)"
              >
                <MenuItem value="">
                  <em>None - Make this a top-level category</em>
                </MenuItem>
                {parentCategories.map((cat) => (
                  <MenuItem key={cat.id} value={cat.id}>
                    {cat.name} ({cat.type})
                  </MenuItem>
                ))}
              </Select>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, px: 1 }}>
                Select a parent category of the same type to create a subcategory. Only 2 levels are supported.
              </Typography>
            </FormControl>

            <TextField
              label="Description"
              value={formData.description}
              onChange={handleInputChange('description')}
              error={!!errors.description}
              helperText={errors.description}
              multiline
              rows={3}
              fullWidth
              disabled={isSubmitting}
            />
          </Box>
        </DialogContent>

        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button 
            onClick={onClose}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Saving...' : mode === 'create' ? 'Create' : 'Save Changes'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};