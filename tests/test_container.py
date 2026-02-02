import pytest
from unittest.mock import Mock
from gravitas.core.container import Container, ServiceDescriptor, container


class TestServiceDescriptor:
    

    def test_service_descriptor_singleton(self):
        
        def factory():
            return "test_instance"

        descriptor = ServiceDescriptor(factory, singleton=True)

        instance1 = descriptor.get_instance(None)
        assert instance1 == "test_instance"

        instance2 = descriptor.get_instance(None)
        assert instance1 is instance2

    def test_service_descriptor_transient(self):
        
        def factory():
            return object()  # Return different objects

        descriptor = ServiceDescriptor(factory, singleton=False)

        instance1 = descriptor.get_instance(None)
        instance2 = descriptor.get_instance(None)
        assert instance1 != instance2
        assert instance1 is not instance2

    def test_service_descriptor_with_class(self):
        
        class TestClass:
            def __init__(self, value="default"):
                self.value = value

        descriptor = ServiceDescriptor(TestClass, singleton=True)
        instance = descriptor.get_instance(None)

        assert isinstance(instance, TestClass)
        assert instance.value == "default"

    def test_service_descriptor_with_dependency_injection(self):
        
        class Dependency:
            pass

        class Service:
            def __init__(self, dep: Dependency):
                self.dep = dep

        container = Container()
        container.register(Dependency, lambda: Dependency())

        descriptor = ServiceDescriptor(Service, singleton=True)
        instance = descriptor.get_instance(container)

        assert isinstance(instance, Service)
        assert isinstance(instance.dep, Dependency)


class TestContainer:
    

    def setup_method(self):
        
        self.container = Container()

    def test_container_initialization(self):
        
        assert self.container._services == {}
        assert self.container._instances == {}

    def test_register_singleton(self):
        
        def factory():
            return "test_service"

        self.container.register(str, factory, singleton=True)

        assert self.container.is_registered(str)
        instance = self.container.resolve(str)
        assert instance == "test_service"

        instance2 = self.container.resolve(str)
        assert instance is instance2

    def test_register_transient(self):
        
        def factory():
            return object()  # Return different objects

        self.container.register(object, factory, singleton=False)

        instance1 = self.container.resolve(object)
        instance2 = self.container.resolve(object)

        assert instance1 != instance2
        assert instance1 is not instance2

    def test_register_singleton_instance(self):
        
        instance = "test_instance"
        self.container.register_singleton(str, instance)

        resolved = self.container.resolve(str)
        assert resolved is instance

    def test_resolve_unregistered_service(self):
        
        result = self.container.resolve(str)
        assert result is None

    def test_is_registered(self):
        
        assert not self.container.is_registered(str)

        self.container.register(str, lambda: "test")
        assert self.container.is_registered(str)

    def test_remove_service(self):
        
        self.container.register(str, lambda: "test")
        assert self.container.is_registered(str)

        self.container.remove(str)
        assert not self.container.is_registered(str)

    def test_remove_singleton_with_cleanup(self):
        
        class TestService:
            def __init__(self):
                self.cleaned = False

            def cleanup(self):
                self.cleaned = True

        service = TestService()
        self.container.register_singleton(TestService, service)

        self.container.remove(TestService)
        assert service.cleaned

    def test_clear_container(self):
        
        class TestService:
            def __init__(self):
                self.cleaned = False

            def cleanup(self):
                self.cleaned = True

        service = TestService()
        self.container.register_singleton(TestService, service)
        self.container.register(str, lambda: "test")

        self.container.clear()

        assert service.cleaned
        assert not self.container.is_registered(TestService)
        assert not self.container.is_registered(str)

    def test_dependency_injection_with_type_hints(self):
        
        class Dependency:
            pass

        class Service:
            def __init__(self, dep: Dependency):
                self.dep = dep

        # Register the dependency first
        self.container.register(Dependency, Dependency)
        self.container.register(Service, Service)

        service = self.container.resolve(Service)
        assert isinstance(service, Service)
        assert isinstance(service.dep, Dependency)

    def test_dependency_injection_missing_dependency(self):
        
        class Service:
            def __init__(self, dep: str):
                self.dep = dep

        self.container.register(Service, Service)

        with pytest.raises(ValueError, match="dependency"):
            self.container.resolve(Service)

    def test_dependency_injection_with_defaults(self):
        
        class Service:
            def __init__(self, value: str = "default"):
                self.value = value

        self.container.register(Service, Service)
        service = self.container.resolve(Service)

        assert service.value == "default"

    def test_thread_safety(self):
        
        import threading
        import time

        results = []

        def worker():
            for i in range(100):
                self.container.register(f"key{i}", lambda: f"value{i}")
                result = self.container.resolve(f"key{i}")
                results.append(result)

        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 500


class TestGlobalContainer:
    

    def test_global_container_exists(self):
        
        assert container is not None
        assert isinstance(container, Container)


if __name__ == "__main__":
    pytest.main([__file__])
