#!/usr/bin/env python3
"""
Example 1: Cooperative Multiple Inheritance & MRO Resolution via super()
Demonstrates how super() traverses the runtime instance's C3-linearized MRO.
"""

class Base:
    def action(self):
        print("  -> Base.action()")

class MixinA(Base):
    def action(self):
        print("  -> MixinA.action() start")
        super().action()
        print("  -> MixinA.action() end")

class MixinB(Base):
    def action(self):
        print("  -> MixinB.action() start")
        super().action()
        print("  -> MixinB.action() end")

class Combined(MixinA, MixinB):
    def action(self):
        print("Combined.action() starting full cooperative chain:")
        super().action()
        print("Combined.action() completed.")

if __name__ == "__main__":
    print(f"MRO: {[cls.__name__ for cls in Combined.__mro__]}")
    c = Combined()
    c.action()
