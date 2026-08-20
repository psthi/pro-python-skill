#!/usr/bin/env python3
"""
Example 4: Static & Runtime Structural Protocols via typing.Protocol (PEP 544)
"""

from typing import Protocol, runtime_checkable

@runtime_checkable
class Closeable(Protocol):
    def close(self) -> None: ...

class CustomDatabaseConnection:
    def close(self) -> None:
        print("Database connection closed cleanly.")

if __name__ == "__main__":
    conn = CustomDatabaseConnection()
    print(f"Is conn Closeable? {isinstance(conn, Closeable)}")
    if isinstance(conn, Closeable):
        conn.close()
