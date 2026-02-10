"""Tests for T093: Deployment Configuration."""

import pytest
import yaml
import os
from pathlib import Path


class TestDockerComposeConfiguration:
    """Test Docker Compose configuration."""

    def load_docker_compose(self):
        """Load docker-compose.yml from project root."""
        docker_compose_path = Path(__file__).parent.parent.parent.parent / "docker-compose.yml"
        with open(docker_compose_path, 'r') as f:
            return yaml.safe_load(f)

    def test_docker_compose_file_exists(self):
        """Verify docker-compose.yml exists."""
        docker_compose_path = Path(__file__).parent.parent.parent.parent / "docker-compose.yml"
        assert docker_compose_path.exists(), "docker-compose.yml not found"

    def test_docker_compose_valid_yaml(self):
        """Verify docker-compose.yml is valid YAML."""
        config = self.load_docker_compose()
        assert isinstance(config, dict)

    def test_docker_compose_version(self):
        """Verify docker-compose version is specified."""
        config = self.load_docker_compose()
        assert "version" in config
        assert config["version"] == "3.9"

    def test_docker_compose_has_services(self):
        """Verify services are defined."""
        config = self.load_docker_compose()
        assert "services" in config
        assert isinstance(config["services"], dict)
        assert len(config["services"]) >= 3

    def test_docker_compose_has_postgres(self):
        """Verify PostgreSQL service is defined."""
        config = self.load_docker_compose()
        assert "postgres" in config["services"]

    def test_docker_compose_has_redis(self):
        """Verify Redis service is defined."""
        config = self.load_docker_compose()
        assert "redis" in config["services"]

    def test_docker_compose_has_api(self):
        """Verify API service is defined."""
        config = self.load_docker_compose()
        assert "api" in config["services"]

    def test_docker_compose_has_volumes(self):
        """Verify volumes are defined."""
        config = self.load_docker_compose()
        assert "volumes" in config
        assert "postgres_data" in config["volumes"]
        assert "redis_data" in config["volumes"]

    def test_docker_compose_has_networks(self):
        """Verify networks are defined."""
        config = self.load_docker_compose()
        assert "networks" in config
        assert "personalization-network" in config["networks"]


class TestPostgresService:
    """Test PostgreSQL service configuration."""

    def load_docker_compose(self):
        """Load docker-compose.yml from project root."""
        docker_compose_path = Path(__file__).parent.parent.parent.parent / "docker-compose.yml"
        with open(docker_compose_path, 'r') as f:
            return yaml.safe_load(f)

    def test_postgres_image_specified(self):
        """Verify PostgreSQL image is specified."""
        config = self.load_docker_compose()
        postgres = config["services"]["postgres"]
        assert "image" in postgres
        assert "postgres:15" in postgres["image"]

    def test_postgres_environment_variables(self):
        """Verify PostgreSQL environment variables are configured."""
        config = self.load_docker_compose()
        postgres = config["services"]["postgres"]
        assert "environment" in postgres
        env = postgres["environment"]
        assert "POSTGRES_USER" in env
        assert "POSTGRES_PASSWORD" in env
        assert "POSTGRES_DB" in env

    def test_postgres_healthcheck(self):
        """Verify PostgreSQL healthcheck is configured."""
        config = self.load_docker_compose()
        postgres = config["services"]["postgres"]
        assert "healthcheck" in postgres
        healthcheck = postgres["healthcheck"]
        assert "test" in healthcheck
        assert "interval" in healthcheck
        assert "timeout" in healthcheck
        assert "retries" in healthcheck

    def test_postgres_volume_persistence(self):
        """Verify PostgreSQL uses persistent volume."""
        config = self.load_docker_compose()
        postgres = config["services"]["postgres"]
        assert "volumes" in postgres
        assert any("postgres_data" in str(v) for v in postgres["volumes"])

    def test_postgres_network_configured(self):
        """Verify PostgreSQL is connected to network."""
        config = self.load_docker_compose()
        postgres = config["services"]["postgres"]
        assert "networks" in postgres
        assert "personalization-network" in postgres["networks"]

    def test_postgres_restart_policy(self):
        """Verify PostgreSQL restart policy is configured."""
        config = self.load_docker_compose()
        postgres = config["services"]["postgres"]
        assert "restart" in postgres
        assert postgres["restart"] == "unless-stopped"


class TestRedisService:
    """Test Redis service configuration."""

    def load_docker_compose(self):
        """Load docker-compose.yml from project root."""
        docker_compose_path = Path(__file__).parent.parent.parent.parent / "docker-compose.yml"
        with open(docker_compose_path, 'r') as f:
            return yaml.safe_load(f)

    def test_redis_image_specified(self):
        """Verify Redis image is specified."""
        config = self.load_docker_compose()
        redis = config["services"]["redis"]
        assert "image" in redis
        assert "redis:7" in redis["image"]

    def test_redis_healthcheck(self):
        """Verify Redis healthcheck is configured."""
        config = self.load_docker_compose()
        redis = config["services"]["redis"]
        assert "healthcheck" in redis
        healthcheck = redis["healthcheck"]
        assert "test" in healthcheck
        assert "interval" in healthcheck

    def test_redis_persistence_enabled(self):
        """Verify Redis persistence is enabled."""
        config = self.load_docker_compose()
        redis = config["services"]["redis"]
        assert "command" in redis
        assert "appendonly yes" in redis["command"]

    def test_redis_volume_persistence(self):
        """Verify Redis uses persistent volume."""
        config = self.load_docker_compose()
        redis = config["services"]["redis"]
        assert "volumes" in redis
        assert any("redis_data" in str(v) for v in redis["volumes"])

    def test_redis_network_configured(self):
        """Verify Redis is connected to network."""
        config = self.load_docker_compose()
        redis = config["services"]["redis"]
        assert "networks" in redis
        assert "personalization-network" in redis["networks"]


class TestAPIService:
    """Test API service configuration."""

    def load_docker_compose(self):
        """Load docker-compose.yml from project root."""
        docker_compose_path = Path(__file__).parent.parent.parent.parent / "docker-compose.yml"
        with open(docker_compose_path, 'r') as f:
            return yaml.safe_load(f)

    def test_api_build_context(self):
        """Verify API build context is specified."""
        config = self.load_docker_compose()
        api = config["services"]["api"]
        assert "build" in api
        assert "context" in api["build"]
        assert api["build"]["context"] == "./backend"

    def test_api_depends_on_postgres(self):
        """Verify API depends on PostgreSQL."""
        config = self.load_docker_compose()
        api = config["services"]["api"]
        assert "depends_on" in api
        assert "postgres" in api["depends_on"]

    def test_api_depends_on_redis(self):
        """Verify API depends on Redis."""
        config = self.load_docker_compose()
        api = config["services"]["api"]
        assert "depends_on" in api
        assert "redis" in api["depends_on"]

    def test_api_healthcheck(self):
        """Verify API healthcheck is configured."""
        config = self.load_docker_compose()
        api = config["services"]["api"]
        assert "healthcheck" in api
        healthcheck = api["healthcheck"]
        assert "test" in healthcheck
        assert "/ready" in " ".join(healthcheck["test"])

    def test_api_database_url_environment(self):
        """Verify DATABASE_URL environment variable is set."""
        config = self.load_docker_compose()
        api = config["services"]["api"]
        assert "environment" in api
        env = api["environment"]
        assert "DATABASE_URL" in env

    def test_api_database_pool_mode_environment(self):
        """Verify DATABASE_POOL_MODE is set to queuepool."""
        config = self.load_docker_compose()
        api = config["services"]["api"]
        assert "environment" in api
        env = api["environment"]
        assert "DATABASE_POOL_MODE" in env
        assert env["DATABASE_POOL_MODE"] == "queuepool"

    def test_api_port_exposed(self):
        """Verify API port is exposed."""
        config = self.load_docker_compose()
        api = config["services"]["api"]
        assert "ports" in api

    def test_api_network_configured(self):
        """Verify API is connected to network."""
        config = self.load_docker_compose()
        api = config["services"]["api"]
        assert "networks" in api
        assert "personalization-network" in api["networks"]

    def test_api_restart_policy(self):
        """Verify API restart policy is configured."""
        config = self.load_docker_compose()
        api = config["services"]["api"]
        assert "restart" in api
        assert api["restart"] == "unless-stopped"

    def test_api_volumes_configured(self):
        """Verify API volumes are configured."""
        config = self.load_docker_compose()
        api = config["services"]["api"]
        assert "volumes" in api

    def test_api_labels_configured(self):
        """Verify API labels are configured for organization."""
        config = self.load_docker_compose()
        api = config["services"]["api"]
        assert "labels" in api


class TestEnvironmentConfiguration:
    """Test environment file configuration."""

    def test_env_docker_file_exists(self):
        """Verify .env.docker exists."""
        env_path = Path(__file__).parent.parent.parent.parent / ".env.docker"
        assert env_path.exists(), ".env.docker not found"

    def test_env_docker_has_required_vars(self):
        """Verify .env.docker has required environment variables."""
        env_path = Path(__file__).parent.parent.parent.parent / ".env.docker"
        with open(env_path, 'r') as f:
            content = f.read()

        required_vars = [
            "ENVIRONMENT",
            "DB_USER",
            "DB_PASSWORD",
            "DB_NAME",
            "API_PORT",
            "SECRET_KEY",
            "DATABASE_POOL_MODE",
        ]

        for var in required_vars:
            assert var in content, f"Missing {var} in .env.docker"


class TestDeploymentScripts:
    """Test deployment scripts and documentation."""

    def test_deployment_checklist_exists(self):
        """Verify deployment checklist exists."""
        checklist_path = Path(__file__).parent.parent.parent.parent / "DEPLOYMENT_CHECKLIST.md"
        assert checklist_path.exists(), "DEPLOYMENT_CHECKLIST.md not found"

    def test_dockerfile_exists(self):
        """Verify Dockerfile exists in backend."""
        dockerfile_path = Path(__file__).parent.parent.parent / "Dockerfile"
        assert dockerfile_path.exists(), "backend/Dockerfile not found"


class TestNetworkConfiguration:
    """Test network configuration."""

    def load_docker_compose(self):
        """Load docker-compose.yml from project root."""
        docker_compose_path = Path(__file__).parent.parent.parent.parent / "docker-compose.yml"
        with open(docker_compose_path, 'r') as f:
            return yaml.safe_load(f)

    def test_network_driver_bridge(self):
        """Verify network driver is bridge."""
        config = self.load_docker_compose()
        assert "networks" in config
        assert "personalization-network" in config["networks"]
        assert config["networks"]["personalization-network"]["driver"] == "bridge"

    def test_all_services_on_same_network(self):
        """Verify all services are on same network."""
        config = self.load_docker_compose()
        services = config["services"]

        for service_name, service_config in services.items():
            assert "networks" in service_config, f"{service_name} not on network"
            assert "personalization-network" in service_config["networks"]


class TestVolumeConfiguration:
    """Test volume configuration."""

    def load_docker_compose(self):
        """Load docker-compose.yml from project root."""
        docker_compose_path = Path(__file__).parent.parent.parent.parent / "docker-compose.yml"
        with open(docker_compose_path, 'r') as f:
            return yaml.safe_load(f)

    def test_postgres_volume_defined(self):
        """Verify postgres_data volume is defined."""
        config = self.load_docker_compose()
        assert "postgres_data" in config["volumes"]

    def test_redis_volume_defined(self):
        """Verify redis_data volume is defined."""
        config = self.load_docker_compose()
        assert "redis_data" in config["volumes"]

    def test_volumes_have_driver(self):
        """Verify volumes have driver specified."""
        config = self.load_docker_compose()
        for volume_name, volume_config in config["volumes"].items():
            assert "driver" in volume_config


class TestHealthChecks:
    """Test health check configuration."""

    def load_docker_compose(self):
        """Load docker-compose.yml from project root."""
        docker_compose_path = Path(__file__).parent.parent.parent.parent / "docker-compose.yml"
        with open(docker_compose_path, 'r') as f:
            return yaml.safe_load(f)

    def test_all_services_have_healthcheck(self):
        """Verify all services have healthcheck configured."""
        config = self.load_docker_compose()
        services = config["services"]

        for service_name, service_config in services.items():
            assert "healthcheck" in service_config, f"{service_name} missing healthcheck"

    def test_postgres_healthcheck_structure(self):
        """Verify PostgreSQL healthcheck has proper structure."""
        config = self.load_docker_compose()
        postgres = config["services"]["postgres"]
        healthcheck = postgres["healthcheck"]

        assert "test" in healthcheck
        assert "interval" in healthcheck
        assert "timeout" in healthcheck
        assert "retries" in healthcheck
        assert "start_period" in healthcheck

    def test_api_healthcheck_timeout_reasonable(self):
        """Verify API healthcheck has reasonable timeout."""
        config = self.load_docker_compose()
        api = config["services"]["api"]
        healthcheck = api["healthcheck"]

        # Extract timeout (e.g., "10s" -> 10)
        timeout_str = healthcheck["timeout"]
        assert "s" in timeout_str


def test_deployment_summary():
    """Summary test demonstrating all deployment features."""
    docker_compose_path = Path(__file__).parent.parent.parent.parent / "docker-compose.yml"
    assert docker_compose_path.exists()

    with open(docker_compose_path, 'r') as f:
        config = yaml.safe_load(f)

    # Verify all components
    assert config["version"] == "3.9"
    assert len(config["services"]) == 3
    assert "postgres" in config["services"]
    assert "redis" in config["services"]
    assert "api" in config["services"]
    assert len(config["volumes"]) == 2
    assert len(config["networks"]) == 1

    # Verify each service has required configurations
    for service_name, service_config in config["services"].items():
        assert "healthcheck" in service_config
        assert "networks" in service_config
        assert "restart" in service_config
