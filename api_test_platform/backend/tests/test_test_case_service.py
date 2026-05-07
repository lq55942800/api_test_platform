"""
Test Case Service Tests - JSON Field Conversion
"""
import pytest
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.base_models import Team, User
from app.models.test_case import TestCase
from app.models.test_case_step import TestCaseStep
from app.models.api import ApiDefinition
from app.services.test_case_service import TestCaseService
from app.schemas.test_case import TestCaseCreate, TestCaseUpdate, TestCaseStepCreate


TEST_DATABASE_URL = "sqlite:///./test_test_case_service.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    """Create database session"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    
    team = Team(id=1, name="Test Team", description="Test team", is_active=True)
    session.add(team)
    
    user = User(id=1, username="testuser", email="test@example.com", password_hash="hash")
    session.add(user)
    
    session.commit()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=engine)


class TestJSONDeserialization:
    """Test JSON deserialization in _convert_test_case method"""
    
    def test_convert_test_case_with_valid_tags(self, db):
        """Test converting test case with valid tags JSON"""
        test_case = TestCase(
            id=1,
            team_id=1,
            name="Test Case",
            tags=json.dumps(["tag1", "tag2"], ensure_ascii=False),
            created_by=1
        )
        db.add(test_case)
        db.commit()
        
        service = TestCaseService(db)
        converted = service._convert_test_case(test_case)
        
        assert converted.tags == ["tag1", "tag2"]
        assert isinstance(converted.tags, list)
    
    def test_convert_test_case_with_valid_variables(self, db):
        """Test converting test case with valid variables JSON"""
        variables = [{"name": "var1", "value": "value1"}]
        test_case = TestCase(
            id=1,
            team_id=1,
            name="Test Case",
            variables=json.dumps(variables, ensure_ascii=False),
            created_by=1
        )
        db.add(test_case)
        db.commit()
        
        service = TestCaseService(db)
        converted = service._convert_test_case(test_case)
        
        assert converted.variables == variables
        assert isinstance(converted.variables, list)
    
    def test_convert_test_case_with_empty_tags(self, db):
        """Test converting test case with empty tags"""
        test_case = TestCase(
            id=1,
            team_id=1,
            name="Test Case",
            tags=None,
            created_by=1
        )
        db.add(test_case)
        db.commit()
        
        service = TestCaseService(db)
        converted = service._convert_test_case(test_case)
        
        assert converted.tags is None
    
    def test_convert_test_case_with_invalid_tags_json(self, db):
        """Test converting test case with invalid tags JSON"""
        test_case = TestCase(
            id=1,
            team_id=1,
            name="Test Case",
            tags="invalid json{",
            created_by=1
        )
        db.add(test_case)
        db.commit()
        
        service = TestCaseService(db)
        converted = service._convert_test_case(test_case)
        
        assert converted.tags == []
    
    def test_convert_step_with_valid_override_headers(self, db):
        """Test converting step with valid override_headers JSON"""
        headers = {"Content-Type": "application/json"}
        step = TestCaseStep(
            id=1,
            test_case_id=1,
            override_headers=json.dumps(headers)
        )
        test_case = TestCase(
            id=1,
            team_id=1,
            name="Test Case",
            created_by=1,
            steps=[step]
        )
        db.add(test_case)
        db.commit()
        
        service = TestCaseService(db)
        converted = service._convert_test_case(test_case)
        
        assert converted.steps[0].override_headers == headers
        assert isinstance(converted.steps[0].override_headers, dict)
    
    def test_convert_step_with_valid_assertions(self, db):
        """Test converting step with valid assertions JSON"""
        assertions = [{"type": "status_code", "expected": 200}]
        step = TestCaseStep(
            id=1,
            test_case_id=1,
            assertions=json.dumps(assertions)
        )
        test_case = TestCase(
            id=1,
            team_id=1,
            name="Test Case",
            created_by=1,
            steps=[step]
        )
        db.add(test_case)
        db.commit()
        
        service = TestCaseService(db)
        converted = service._convert_test_case(test_case)
        
        assert converted.steps[0].assertions == assertions
        assert isinstance(converted.steps[0].assertions, list)
    
    def test_convert_step_with_invalid_json(self, db):
        """Test converting step with invalid JSON field"""
        step = TestCaseStep(
            id=1,
            test_case_id=1,
            override_headers="invalid json{"
        )
        test_case = TestCase(
            id=1,
            team_id=1,
            name="Test Case",
            created_by=1,
            steps=[step]
        )
        db.add(test_case)
        db.commit()
        
        service = TestCaseService(db)
        converted = service._convert_test_case(test_case)
        
        assert converted.steps[0].override_headers is None
    
    def test_convert_step_with_all_json_fields(self, db):
        """Test converting step with all JSON fields"""
        headers = {"Content-Type": "application/json"}
        params = {"key": "value"}
        body = {"data": "test"}
        cookies = [{"name": "session", "value": "abc123"}]
        assertions = [{"type": "status_code", "expected": 200}]
        extractors = [{"type": "jsonpath", "path": "$.data.id"}]
        timeout = {"connect": 5000, "read": 10000}
        condition = {"type": "variable", "variable": "enabled", "operator": "==", "value": "true"}
        
        step = TestCaseStep(
            id=1,
            test_case_id=1,
            override_headers=json.dumps(headers),
            override_params=json.dumps(params),
            override_body=json.dumps(body),
            override_cookies=json.dumps(cookies),
            assertions=json.dumps(assertions),
            extractors=json.dumps(extractors),
            timeout_config=json.dumps(timeout),
            execution_condition=json.dumps(condition)
        )
        test_case = TestCase(
            id=1,
            team_id=1,
            name="Test Case",
            created_by=1,
            steps=[step]
        )
        db.add(test_case)
        db.commit()
        
        service = TestCaseService(db)
        converted = service._convert_test_case(test_case)
        
        assert converted.steps[0].override_headers == headers
        assert converted.steps[0].override_params == params
        assert converted.steps[0].override_body == body
        assert converted.steps[0].override_cookies == cookies
        assert converted.steps[0].assertions == assertions
        assert converted.steps[0].extractors == extractors
        assert converted.steps[0].timeout_config == timeout
        assert converted.steps[0].execution_condition == condition


class TestJSONSerialization:
    """Test JSON serialization in create_test_case and update_test_case methods"""
    
    def test_create_test_case_with_tags(self, db):
        """Test creating test case with tags"""
        service = TestCaseService(db)
        
        test_case_data = TestCaseCreate(
            name="Test Case",
            tags=["tag1", "tag2"],
            steps=[]
        )
        
        created = service.create_test_case(test_case_data, team_id=1, user_id=1)
        
        assert created.tags == ["tag1", "tag2"]
        assert isinstance(created.tags, list)
        
        db_test_case = db.query(TestCase).filter(TestCase.id == created.id).first()
        assert json.loads(db_test_case.tags) == ["tag1", "tag2"]
    
    def test_create_test_case_with_variables(self, db):
        """Test creating test case with variables"""
        service = TestCaseService(db)
        
        variables = [{"name": "var1", "value": "value1"}]
        test_case_data = TestCaseCreate(
            name="Test Case",
            variables=variables,
            steps=[]
        )
        
        created = service.create_test_case(test_case_data, team_id=1, user_id=1)
        
        assert created.variables == variables
        assert isinstance(created.variables, list)
        
        db_test_case = db.query(TestCase).filter(TestCase.id == created.id).first()
        assert json.loads(db_test_case.variables) == variables
    
    def test_create_test_case_with_step_json_fields(self, db):
        """Test creating test case with step containing JSON fields"""
        service = TestCaseService(db)
        
        step_data = TestCaseStepCreate(
            step_type="api",
            override_headers={"Content-Type": "application/json"},
            override_params={"key": "value"},
            override_body=json.dumps({"data": "test"}),
            override_cookies=[{"name": "session", "value": "abc123"}],
            assertions=[{"type": "status_code", "expected": 200}],
            extractors=[{"type": "jsonpath", "path": "$.data.id"}],
            timeout_config={"connect": 5000, "read": 10000},
            execution_condition={"type": "variable", "variable": "enabled"}
        )
        
        test_case_data = TestCaseCreate(
            name="Test Case",
            steps=[step_data]
        )
        
        created = service.create_test_case(test_case_data, team_id=1, user_id=1)
        
        assert created.steps[0].override_headers == {"Content-Type": "application/json"}
        assert created.steps[0].override_params == {"key": "value"}
        assert created.steps[0].override_body == {"data": "test"}
        assert created.steps[0].override_cookies == [{"name": "session", "value": "abc123"}]
        assert created.steps[0].assertions == [{"type": "status_code", "expected": 200}]
        assert created.steps[0].extractors == [{"type": "jsonpath", "path": "$.data.id"}]
        assert created.steps[0].timeout_config == {"connect": 5000, "read": 10000}
        assert created.steps[0].execution_condition == {"type": "variable", "variable": "enabled"}
        
        db_step = db.query(TestCaseStep).filter(TestCaseStep.test_case_id == created.id).first()
        assert json.loads(db_step.override_headers) == {"Content-Type": "application/json"}
        assert json.loads(db_step.assertions) == [{"type": "status_code", "expected": 200}]
    
    def test_update_test_case_with_tags(self, db):
        """Test updating test case tags"""
        test_case = TestCase(
            id=1,
            team_id=1,
            name="Test Case",
            tags=json.dumps(["old_tag"]),
            created_by=1
        )
        db.add(test_case)
        db.commit()
        
        service = TestCaseService(db)
        
        update_data = TestCaseUpdate(
            tags=["new_tag1", "new_tag2"]
        )
        
        updated = service.update_test_case(1, update_data, user_id=1)
        
        assert updated.tags == ["new_tag1", "new_tag2"]
        
        db_test_case = db.query(TestCase).filter(TestCase.id == 1).first()
        assert json.loads(db_test_case.tags) == ["new_tag1", "new_tag2"]
    
    def test_update_test_case_with_step_json_fields(self, db):
        """Test updating test case with step JSON fields"""
        test_case = TestCase(
            id=1,
            team_id=1,
            name="Test Case",
            created_by=1
        )
        db.add(test_case)
        db.commit()
        
        service = TestCaseService(db)
        
        step_data = TestCaseStepCreate(
            step_type="api",
            override_headers={"Authorization": "Bearer token"},
            assertions=[{"type": "jsonpath", "path": "$.success", "expected": True}]
        )
        
        update_data = TestCaseUpdate(
            steps=[step_data]
        )
        
        updated = service.update_test_case(1, update_data, user_id=1)
        
        assert updated.steps[0].override_headers == {"Authorization": "Bearer token"}
        assert updated.steps[0].assertions == [{"type": "jsonpath", "path": "$.success", "expected": True}]
        
        db_step = db.query(TestCaseStep).filter(TestCaseStep.test_case_id == 1).first()
        assert json.loads(db_step.override_headers) == {"Authorization": "Bearer token"}
        assert json.loads(db_step.assertions) == [{"type": "jsonpath", "path": "$.success", "expected": True}]
    
    def test_create_test_case_with_chinese_characters(self, db):
        """Test creating test case with Chinese characters in JSON fields"""
        service = TestCaseService(db)
        
        test_case_data = TestCaseCreate(
            name="测试用例",
            tags=["标签1", "标签2"],
            variables=[{"name": "变量1", "value": "值1"}],
            steps=[]
        )
        
        created = service.create_test_case(test_case_data, team_id=1, user_id=1)
        
        assert created.tags == ["标签1", "标签2"]
        assert created.variables == [{"name": "变量1", "value": "值1"}]
        
        db_test_case = db.query(TestCase).filter(TestCase.id == created.id).first()
        assert json.loads(db_test_case.tags) == ["标签1", "标签2"]
        assert json.loads(db_test_case.variables) == [{"name": "变量1", "value": "值1"}]


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_convert_test_case_with_none_values(self, db):
        """Test converting test case with None values"""
        test_case = TestCase(
            id=1,
            team_id=1,
            name="Test Case",
            tags=None,
            variables=None,
            created_by=1
        )
        db.add(test_case)
        db.commit()
        
        service = TestCaseService(db)
        converted = service._convert_test_case(test_case)
        
        assert converted.tags is None
        assert converted.variables is None
    
    def test_convert_step_with_none_json_fields(self, db):
        """Test converting step with None JSON fields"""
        step = TestCaseStep(
            id=1,
            test_case_id=1,
            override_headers=None,
            assertions=None
        )
        test_case = TestCase(
            id=1,
            team_id=1,
            name="Test Case",
            created_by=1,
            steps=[step]
        )
        db.add(test_case)
        db.commit()
        
        service = TestCaseService(db)
        converted = service._convert_test_case(test_case)
        
        assert converted.steps[0].override_headers is None
        assert converted.steps[0].assertions is None
    
    def test_create_test_case_with_empty_lists(self, db):
        """Test creating test case with empty lists"""
        service = TestCaseService(db)
        
        test_case_data = TestCaseCreate(
            name="Test Case",
            tags=[],
            variables=[],
            steps=[]
        )
        
        created = service.create_test_case(test_case_data, team_id=1, user_id=1)
        
        assert created.tags == []
        assert created.variables == []
        
        db_test_case = db.query(TestCase).filter(TestCase.id == created.id).first()
        assert json.loads(db_test_case.tags) == []
        assert json.loads(db_test_case.variables) == []
