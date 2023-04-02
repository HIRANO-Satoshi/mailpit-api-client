import logging
import pathlib

import tomli
import invoke as inv
import tests.unit.tasks as ut
import tests.integration.tasks as it
import logging518.config

PROJECT_NAME = "mailpit-api-client"
DOCKER_COMPOSE_PATH = "tests/docker/docker-compose.yml"

logging518.config.fileConfig("pyproject.toml")
namespace = inv.Collection()


def read_pyproject_toml():
    with open("pyproject.toml", "rb") as fp:
        config = tomli.load(fp)
    return config["tool"]["invoke"]["test"]


def build_containers(c: inv.Context, profile: str):
    config = read_pyproject_toml()
    for python_version in config["python_versions"]:
        project_name = f"{PROJECT_NAME}-{python_version.replace('.', '')}"
        env = {"PYTHON_VERSION": python_version}

        c.run(
            (
                f"docker-compose -p {project_name} "
                f"--profile {profile} -f {DOCKER_COMPOSE_PATH} build"
            ),
            env=env,
        )


@inv.task
def unit(c: inv.Context):
    logger = logging.getLogger("test_runner.unit")
    logger.info("unit testing started")

    config = read_pyproject_toml()
    profile = "unittest"
    tools = ["black", "lint", "mypy", "unittest"]

    for python_version in config["python_versions"]:
        logger.info(f"running with Python {python_version}")
        project_name = f"{PROJECT_NAME}-{python_version.replace('.', '')}"
        env = {"PYTHON_VERSION": python_version}
        logger.debug(f"set environment variables to: {env}")
        for tool in tools:
            logger.info(f"Running tool in container: {tool}")
            ut.run_tool_in_container(c, env, profile, project_name, tool)


@inv.task
def integration(c: inv.Context):
    logger = logging.getLogger("test_runner.integration")
    logger.info("integration testing started")
    config = read_pyproject_toml()
    profile = "integration"
    path = pathlib.Path("tests/integration")
    for python_version in config["python_versions"]:
        logger.info(f"running with Python {python_version}")
        for file in path.iterdir():
            if file.name.startswith("test"):
                logger.info(f"running tests in file {file}")
                project_name = f"{PROJECT_NAME}-{python_version.replace('.', '')}"
                env = {
                    "PYTHON_VERSION": python_version,
                    "TEST_FILE": str(file),
                    "PYTHONTRACEMALLOC": "1",
                }
                logger.debug(f"set environment variables to: {env}")

                it.run_test(c, env, profile, project_name, file)


@inv.task
def unittest_build(c: inv.Context):
    profile = "integration"
    build_containers(c, profile)


@inv.task
def integration_build(c: inv.Context):
    profile = "integration"
    build_containers(c, profile)


tests = inv.Collection("tests")

tests.add_task(unit)
tests.add_task(integration)

docker = inv.Collection("docker")
build = inv.Collection("build")
build.add_task(integration_build, name="integration")
build.add_task(unittest_build, name="unit")

docker.add_collection(build)

namespace.add_collection(tests)
namespace.add_collection(docker)
