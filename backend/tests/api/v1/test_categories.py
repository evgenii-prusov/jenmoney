import pytest
from fastapi.testclient import TestClient


class TestCategoryCreate:
    def test_create_category_with_all_fields(self, client: TestClient) -> None:
        category_data = {
            "name": "Food & Dining",
            "description": "Restaurants, groceries, and food-related expenses"
        }
        response = client.post("/api/v1/categories/", json=category_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == category_data["name"]
        assert data["description"] == category_data["description"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_category_minimal_fields(self, client: TestClient) -> None:
        category_data = {"name": "Transportation"}
        response = client.post("/api/v1/categories/", json=category_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == category_data["name"]
        assert data["description"] is None

    def test_create_category_empty_name(self, client: TestClient) -> None:
        category_data = {"name": ""}
        response = client.post("/api/v1/categories/", json=category_data)
        assert response.status_code == 422

    def test_create_category_name_too_long(self, client: TestClient) -> None:
        category_data = {"name": "a" * 101}  # More than 100 characters
        response = client.post("/api/v1/categories/", json=category_data)
        assert response.status_code == 422


class TestCategoryList:
    def test_get_categories_empty(self, client: TestClient) -> None:
        response = client.get("/api/v1/categories/")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["pages"] == 1

    def test_get_categories_with_data(self, client: TestClient) -> None:
        # Create test categories
        category1 = {"name": "Food", "description": "Food expenses"}
        category2 = {"name": "Travel", "description": "Travel expenses"}
        
        client.post("/api/v1/categories/", json=category1)
        client.post("/api/v1/categories/", json=category2)
        
        response = client.get("/api/v1/categories/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2
        assert data["page"] == 1
        assert data["pages"] == 1


class TestCategoryGet:
    def test_get_category_by_id(self, client: TestClient) -> None:
        # Create a category first
        category_data = {"name": "Entertainment", "description": "Movies, games, etc."}
        create_response = client.post("/api/v1/categories/", json=category_data)
        created_category = create_response.json()
        
        # Get the category by ID
        response = client.get(f"/api/v1/categories/{created_category['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_category["id"]
        assert data["name"] == category_data["name"]
        assert data["description"] == category_data["description"]

    def test_get_category_not_found(self, client: TestClient) -> None:
        response = client.get("/api/v1/categories/99999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Category not found"


class TestCategoryUpdate:
    def test_update_category_all_fields(self, client: TestClient) -> None:
        # Create a category first
        category_data = {"name": "Shopping", "description": "General shopping"}
        create_response = client.post("/api/v1/categories/", json=category_data)
        created_category = create_response.json()
        
        # Update the category
        update_data = {"name": "Online Shopping", "description": "E-commerce purchases"}
        response = client.patch(f"/api/v1/categories/{created_category['id']}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]

    def test_update_category_partial(self, client: TestClient) -> None:
        # Create a category first
        category_data = {"name": "Health", "description": "Medical expenses"}
        create_response = client.post("/api/v1/categories/", json=category_data)
        created_category = create_response.json()
        
        # Update only the name
        update_data = {"name": "Healthcare"}
        response = client.patch(f"/api/v1/categories/{created_category['id']}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == category_data["description"]  # Should remain unchanged

    def test_update_category_not_found(self, client: TestClient) -> None:
        update_data = {"name": "Non-existent"}
        response = client.patch("/api/v1/categories/99999", json=update_data)
        assert response.status_code == 404


class TestCategoryDelete:
    def test_delete_category(self, client: TestClient) -> None:
        # Create a category first
        category_data = {"name": "Utilities", "description": "Electricity, water, etc."}
        create_response = client.post("/api/v1/categories/", json=category_data)
        created_category = create_response.json()
        
        # Delete the category
        response = client.delete(f"/api/v1/categories/{created_category['id']}")
        assert response.status_code == 200
        
        # Verify it's deleted
        get_response = client.get(f"/api/v1/categories/{created_category['id']}")
        assert get_response.status_code == 404

    def test_delete_category_not_found(self, client: TestClient) -> None:
        response = client.delete("/api/v1/categories/99999")
        assert response.status_code == 404


class TestCategoryIntegration:
    def test_full_crud_workflow(self, client: TestClient) -> None:
        # Create
        category_data = {"name": "Education", "description": "Books, courses, training"}
        create_response = client.post("/api/v1/categories/", json=category_data)
        assert create_response.status_code == 200
        created_category = create_response.json()
        
        # Read
        get_response = client.get(f"/api/v1/categories/{created_category['id']}")
        assert get_response.status_code == 200
        
        # Update
        update_data = {"name": "Learning", "description": "Educational materials"}
        update_response = client.patch(f"/api/v1/categories/{created_category['id']}", json=update_data)
        assert update_response.status_code == 200
        updated_category = update_response.json()
        assert updated_category["name"] == update_data["name"]
        
        # Delete
        delete_response = client.delete(f"/api/v1/categories/{created_category['id']}")
        assert delete_response.status_code == 200
        
        # Verify deletion
        final_get_response = client.get(f"/api/v1/categories/{created_category['id']}")
        assert final_get_response.status_code == 404