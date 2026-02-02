# Dependency injection container - avoids singleton pattern, reduces coupling
from typing import Dict, Type, Any, Callable, Optional, TypeVar, Generic, get_type_hints
from inspect import isclass, isfunction, ismethod
import threading

T = TypeVar('T')

class ServiceDescriptor:
    def __init__(self, factory: Callable, singleton: bool = True):
        self.factory = factory
        self.singleton = singleton
        self.instance = None if singleton else None
        self._lock = threading.Lock()

    def get_instance(self, container: 'Container') -> Any:
        if not self.singleton:
            return self._create_instance(container)

        with self._lock:
            if self.instance is None:
                self.instance = self._create_instance(container)
            return self.instance

    def _create_instance(self, container: 'Container') -> Any:
        if isclass(self.factory):
            # class - resolve constructor params and auto inject
            return self._create_with_injection(container, self.factory)
        else:
            # factory function - call it and auto inject params
            return self._create_with_injection(container, self.factory)

    def _create_with_injection(self, container: 'Container', factory: Callable) -> Any:
        # get type hints for function or class
        if isclass(factory):
            hints = get_type_hints(factory.__init__)
        else:
            hints = get_type_hints(factory)

        # get param list
        if isclass(factory):
            import inspect
            params = inspect.signature(factory.__init__).parameters
        else:
            import inspect
            params = inspect.signature(factory).parameters

        # prepare kwargs
        kwargs = {}

        for name, param in params.items():
            if name == 'self':
                continue

            # check for type hint
            param_type = hints.get(name)
            if param_type:
                # try to resolve dependency from container
                dependency = container.resolve(param_type)
                if dependency is not None:
                    kwargs[name] = dependency
                elif param.default is inspect.Parameter.empty:
                    # no default and cant resolve - throw error
                    raise ValueError(f"Cannot resolve dependency: {name} ({param_type})")
            elif param.default is not inspect.Parameter.empty:
                # no type hint but has default - use default
                kwargs[name] = param.default

        # create instance
        if isclass(factory):
            return factory(**kwargs)
        else:
            return factory(**kwargs)

class Container:
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._instances: Dict[Type, Any] = {}
        self._lock = threading.RLock()

    def register(self, service_type: Type[T], factory: Callable, singleton: bool = True) -> None:
        with self._lock:
            self._services[service_type] = ServiceDescriptor(factory, singleton)

    def register_singleton(self, service_type: Type[T], instance: T) -> None:
        with self._lock:
            descriptor = ServiceDescriptor(lambda: instance, singleton=True)
            descriptor.instance = instance
            self._services[service_type] = descriptor
            self._instances[service_type] = instance

    def register_transient(self, service_type: Type[T], factory: Callable) -> None:
        # transient - creates new instance each time
        with self._lock:
            self._services[service_type] = ServiceDescriptor(factory, singleton=False)

    def resolve(self, service_type: Type[T]) -> Optional[T]:
        with self._lock:
            if service_type not in self._services:
                return None

            descriptor = self._services[service_type]
            return descriptor.get_instance(self)

    def is_registered(self, service_type: Type[T]) -> bool:
        with self._lock:
            return service_type in self._services

    def remove(self, service_type: Type[T]) -> None:
        with self._lock:
            if service_type in self._services:
                descriptor = self._services.pop(service_type)
                if descriptor.singleton and descriptor.instance is not None:
                    # singleton with instance - try calling cleanup
                    instance = descriptor.instance
                    if hasattr(instance, 'cleanup'):
                        try:
                            instance.cleanup()
                        except Exception:
                            pass
                if service_type in self._instances:
                    self._instances.pop(service_type)

    def clear(self) -> None:
        with self._lock:
            # cleanup all singleton instances
            for service_type, descriptor in self._services.items():
                if descriptor.singleton and descriptor.instance is not None:
                    instance = descriptor.instance
                    if hasattr(instance, 'cleanup'):
                        try:
                            instance.cleanup()
                        except Exception:
                            pass
                    self._instances.pop(service_type, None)

            # clear all service descriptors
            self._services.clear()

# global container instance
container = Container()
