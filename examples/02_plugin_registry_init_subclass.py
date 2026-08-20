#!/usr/bin/env python3
"""
Example 2: Modern Zero-Metaclass Plugin Registry via __init_subclass__ (PEP 487)
"""

class Serializer:
    _registry: dict[str, type["Serializer"]] = {}

    @classmethod
    def __init_subclass__(cls, format_name: str | None = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if format_name:
            cls._registry[format_name] = cls

    @classmethod
    def get_serializer(cls, format_name: str) -> type["Serializer"]:
        return cls._registry[format_name]

class JSONSerializer(Serializer, format_name="json"):
    def serialize(self, data): return f'{{"json": {data}}}'

class XMLSerializer(Serializer, format_name="xml"):
    def serialize(self, data): return f'<xml>{data}</xml>'

if __name__ == "__main__":
    print(f"Registered Serializers: {list(Serializer._registry.keys())}")
    s = Serializer.get_serializer("json")()
    print("Execution:", s.serialize("test_data"))
