import pytest
from fastapi.testclient import TestClient


class TestCategoryCreate:
    def test_create_category_with_all_fields(self, client: TestClient) -> None:
        category_data = {
            "name": "Food & Dining",
            "description": "Restaurants, groceries, and food-related expenses",
            "type": "expense"
        }
        response = client.post("/api/v1/categories/", json=category_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == category_data["name"]
        assert data["description"] == category_data["description"]
        assert data["parent_id"] is None
        assert data["children"] == []
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_category_minimal_fields(self, client: TestClient) -> None:
        category_data = {"name": "Transportation", "type": "expense"}
        response = client.post("/api/v1/categories/", json=category_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == category_data["name"]
        assert data["description"] is None
        assert data["parent_id"] is None

    def test_create_subcategory(self, client: TestClient) -> None:
        # Create parent category first
        parent_data = {"name": "Food", "description": "Food expenses", "type": "expense"}
        parent_response = client.post("/api/v1/categories/", json=parent_data)
        assert parent_response.status_code == 200
        parent_category = parent_response.json()
        
        # Create subcategory
        subcategory_data = {
            "name": "Restaurants",
            "description": "Dining out expenses",
            "type": "expense",
            "parent_id": parent_category["id"]
        }
        response = client.post("/api/v1/categories/", json=subcategory_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == subcategory_data["name"]
        assert data["parent_id"] == parent_category["id"]

    def test_create_category_with_invalid_parent(self, client: TestClient) -> None:
        category_data = {
            "name": "Invalid Child",
            "type": "expense",
            "parent_id": 99999  # Non-existent parent
        }
        response = client.post("/api/v1/categories/", json=category_data)
        assert response.status_code == 400
        assert "Parent category not found" in response.json()["detail"]

    def test_create_category_three_levels_not_allowed(self, client: TestClient) -> None:
        # Create grandparent
        grandparent_data = {"name": "Expenses", "type": "expense"}
        grandparent_response = client.post("/api/v1/categories/", json=grandparent_data)
        grandparent = grandparent_response.json()
        
        # Create parent
        parent_data = {"name": "Food", "type": "expense", "parent_id": grandparent["id"]}
        parent_response = client.post("/api/v1/categories/", json=parent_data)
        parent = parent_response.json()
        
        # Try to create grandchild (should fail)
        grandchild_data = {"name": "Restaurants", "type": "expense", "parent_id": parent["id"]}
        response = client.post("/api/v1/categories/", json=grandchild_data)
        assert response.status_code == 400
        assert "Cannot create more than 2 levels" in response.json()["detail"]

    def test_create_category_empty_name(self, client: TestClient) -> None:
        category_data = {"name": "", "type": "expense"}
        response = client.post("/api/v1/categories/", json=category_data)
        assert response.status_code == 422

    def test_create_category_name_too_long(self, client: TestClient) -> None:
        category_data = {"name": "a" * 101, "type": "expense"}  # More than 100 characters
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
        category1 = {"name": "Food", "description": "Food expenses", "type": "expense"}
        category2 = {"name": "Travel", "description": "Travel expenses", "type": "expense"}
        
        client.post("/api/v1/categories/", json=category1)
        client.post("/api/v1/categories/", json=category2)
        
        response = client.get("/api/v1/categories/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2
        assert data["page"] == 1
        assert data["pages"] == 1

    def test_get_categories_hierarchical(self, client: TestClient) -> None:
        # Create parent and child categories
        parent_data = {"name": "Food", "description": "Food expenses", "type": "expense"}
        parent_response = client.post("/api/v1/categories/", json=parent_data)
        parent = parent_response.json()
        
        child_data = {"name": "Restaurants", "type": "expense", "parent_id": parent["id"]}
        client.post("/api/v1/categories/", json=child_data)
        
        # Test regular list (should return both)
        response = client.get("/api/v1/categories/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2
        
        # Test hierarchical list (should return only parent with children)
        response = client.get("/api/v1/categories/?hierarchical=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1  # Only parent category
        assert data["total"] == 1
        assert len(data["items"][0]["children"]) == 1  # Parent has one child

    def test_get_categories_hierarchy_endpoint(self, client: TestClient) -> None:
        # Create parent and child categories
        parent_data = {"name": "Food", "description": "Food expenses", "type": "expense"}
        parent_response = client.post("/api/v1/categories/", json=parent_data)
        parent = parent_response.json()
        
        child_data = {"name": "Restaurants", "type": "expense", "parent_id": parent["id"]}
        client.post("/api/v1/categories/", json=child_data)
        
        # Test hierarchy endpoint
        response = client.get("/api/v1/categories/hierarchy")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1  # Only parent category
        assert data[0]["name"] == "Food"
        assert len(data[0]["children"]) == 1
        assert data[0]["children"][0]["name"] == "Restaurants"


class TestCategoryGet:
    def test_get_category_by_id(self, client: TestClient) -> None:
        # Create a category first
        category_data = {"name": "Entertainment", "description": "Movies, games, etc.", "type": "expense"}
        create_response = client.post("/api/v1/categories/", json=category_data)
        created_category = create_response.json()
        
        # Get the category by ID
        response = client.get(f"/api/v1/categories/{created_category['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_category["id"]
        assert data["name"] == category_data["name"]
        assert data["description"] == category_data["description"]
        assert data["children"] == []

    def test_get_category_with_children(self, client: TestClient) -> None:
        # Create parent category
        parent_data = {"name": "Food", "description": "Food expenses", "type": "expense"}
        parent_response = client.post("/api/v1/categories/", json=parent_data)
        parent = parent_response.json()
        
        # Create child category
        child_data = {"name": "Restaurants", "type": "expense", "parent_id": parent["id"]}
        client.post("/api/v1/categories/", json=child_data)
        
        # Get parent category - should include children
        response = client.get(f"/api/v1/categories/{parent['id']}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["children"]) == 1
        assert data["children"][0]["name"] == "Restaurants"

    def test_get_category_not_found(self, client: TestClient) -> None:
        response = client.get("/api/v1/categories/99999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Category not found"


class TestCategoryUpdate:
    def test_update_category_all_fields(self, client: TestClient) -> None:
        # Create a category first
        category_data = {"name": "Shopping", "description": "General shopping", "type": "expense"}
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
        category_data = {"name": "Health", "description": "Medical expenses", "type": "expense"}
        create_response = client.post("/api/v1/categories/", json=category_data)
        created_category = create_response.json()
        
        # Update only the name
        update_data = {"name": "Healthcare", "type": "expense"}
        response = client.patch(f"/api/v1/categories/{created_category['id']}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == category_data["description"]  # Should remain unchanged

    def test_update_category_change_parent(self, client: TestClient) -> None:
        # Create two parent categories
        parent1_data = {"name": "Food", "type": "expense"}
        parent1_response = client.post("/api/v1/categories/", json=parent1_data)
        parent1 = parent1_response.json()
        
        parent2_data = {"name": "Entertainment", "type": "expense"}
        parent2_response = client.post("/api/v1/categories/", json=parent2_data)
        parent2 = parent2_response.json()
        
        # Create child category under parent1
        child_data = {"name": "Restaurants", "type": "expense", "parent_id": parent1["id"]}
        child_response = client.post("/api/v1/categories/", json=child_data)
        child = child_response.json()
        
        # Move child to parent2
        update_data = {"parent_id": parent2["id"]}
        response = client.patch(f"/api/v1/categories/{child['id']}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["parent_id"] == parent2["id"]

    def test_update_category_prevent_self_parent(self, client: TestClient) -> None:
        # Create a category
        category_data = {"name": "Food", "type": "expense"}
        create_response = client.post("/api/v1/categories/", json=category_data)
        category = create_response.json()
        
        # Try to make it its own parent
        update_data = {"parent_id": category["id"]}
        response = client.patch(f"/api/v1/categories/{category['id']}", json=update_data)
        assert response.status_code == 400
        assert "cannot be its own parent" in response.json()["detail"]

    def test_update_category_prevent_circular_relationship(self, client: TestClient) -> None:
        # Create parent and child
        parent_data = {"name": "Food", "type": "expense"}
        parent_response = client.post("/api/v1/categories/", json=parent_data)
        parent = parent_response.json()
        
        child_data = {"name": "Restaurants", "type": "expense", "parent_id": parent["id"]}
        child_response = client.post("/api/v1/categories/", json=child_data)
        child = child_response.json()
        
        # Try to make parent a child of its own child
        update_data = {"parent_id": child["id"]}
        response = client.patch(f"/api/v1/categories/{parent['id']}", json=update_data)
        assert response.status_code == 400
        assert "Cannot set a child category as parent" in response.json()["detail"]

    def test_update_category_not_found(self, client: TestClient) -> None:
        update_data = {"name": "Non-existent", "type": "expense"}
        response = client.patch("/api/v1/categories/99999", json=update_data)
        assert response.status_code == 404


class TestCategoryDelete:
    def test_delete_category(self, client: TestClient) -> None:
        # Create a category first
        category_data = {"name": "Utilities", "description": "Electricity, water, etc.", "type": "expense"}
        create_response = client.post("/api/v1/categories/", json=category_data)
        created_category = create_response.json()
        
        # Delete the category
        response = client.delete(f"/api/v1/categories/{created_category['id']}")
        assert response.status_code == 200
        
        # Verify it's deleted
        get_response = client.get(f"/api/v1/categories/{created_category['id']}")
        assert get_response.status_code == 404

    def test_delete_category_with_children(self, client: TestClient) -> None:
        # Create parent and child categories
        parent_data = {"name": "Food", "type": "expense"}
        parent_response = client.post("/api/v1/categories/", json=parent_data)
        parent = parent_response.json()
        
        child_data = {"name": "Restaurants", "type": "expense", "parent_id": parent["id"]}
        child_response = client.post("/api/v1/categories/", json=child_data)
        child = child_response.json()
        
        # Delete parent (should also delete child due to cascade)
        response = client.delete(f"/api/v1/categories/{parent['id']}")
        assert response.status_code == 200
        
        # Verify both are deleted
        parent_get_response = client.get(f"/api/v1/categories/{parent['id']}")
        assert parent_get_response.status_code == 404
        
        child_get_response = client.get(f"/api/v1/categories/{child['id']}")
        assert child_get_response.status_code == 404

    def test_delete_category_not_found(self, client: TestClient) -> None:
        response = client.delete("/api/v1/categories/99999")
        assert response.status_code == 404


class TestCategoryIntegration:
    def test_full_crud_workflow(self, client: TestClient) -> None:
        # Create
        category_data = {"name": "Education", "description": "Books, courses, training", "type": "expense"}
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

    def test_hierarchical_crud_workflow(self, client: TestClient) -> None:
        # Create parent category
        parent_data = {"name": "Питание", "description": "Расходы на питание", "type": "expense"}
        parent_response = client.post("/api/v1/categories/", json=parent_data)
        assert parent_response.status_code == 200
        parent = parent_response.json()
        
        # Create child categories
        children_data = [
            {"name": "Продукты", "description": "Покупка продуктов", "type": "expense", "parent_id": parent["id"]},
            {"name": "Готовая еда", "description": "Заказ еды", "type": "expense", "parent_id": parent["id"]},
            {"name": "Рестораны", "description": "Посещение ресторанов", "type": "expense", "parent_id": parent["id"]},
        ]
        
        children = []
        for child_data in children_data:
            child_response = client.post("/api/v1/categories/", json=child_data)
            assert child_response.status_code == 200
            children.append(child_response.json())
        
        # Test hierarchy endpoint
        hierarchy_response = client.get("/api/v1/categories/hierarchy")
        assert hierarchy_response.status_code == 200
        hierarchy_data = hierarchy_response.json()
        
        assert len(hierarchy_data) == 1
        assert hierarchy_data[0]["name"] == "Питание"
        assert len(hierarchy_data[0]["children"]) == 3
        
        child_names = [child["name"] for child in hierarchy_data[0]["children"]]
        assert "Продукты" in child_names
        assert "Готовая еда" in child_names
        assert "Рестораны" in child_names