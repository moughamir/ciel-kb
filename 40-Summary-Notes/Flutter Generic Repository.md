# Flutter Generic Repository

This note summarizes the discussion and implementation details for creating a generic repository in Flutter, including integration with Supabase.

## Generic Repository Concept

A generic repository provides a standardized way to interact with data sources, abstracting away the underlying data access logic. It typically includes methods for adding, updating, deleting, and retrieving data.

## Optimized Implementation (In-memory)

A basic in-memory implementation using a `List<T>`:

```dart
import 'package:flutter/foundation.dart';

class GenericRepository<T> {
  List<T> _items = [];

  void add(T item) {
    _items.add(item);
  }

  void update(T item) {
    final index = _items.indexOf(item);
    _items[index] = item;
  }

  void delete(T item) {
    _items.remove(item);
  }

  T get(int index) {
    return _items[index];
  }

  int get count {
    return _items.length;
  }

  List<T> get all {
    return List.unmodifiable(_items);
  }
}
```

## Supabase Integration

To integrate the `GenericRepository` with Supabase:

1.  **Install `supabase_client`:** Add `supabase_client: ^0.4.4` to `pubspec.yaml`.
2.  **Import:** `import 'package:supabase_client/supabase_client.dart';`
3.  **Initialize `SupabaseClient`:** Pass an instance of `SupabaseClient` to the `GenericRepository` constructor.
4.  **Implement CRUD with Supabase:** Use `_client.insert`, `_client.update`, `_client.delete`, and `_client.select` methods for data operations.

```dart
import 'package:supabase_client/supabase_client.dart';

class GenericRepository<T> {
  final SupabaseClient _client;

  GenericRepository(this._client);

  void add(T item) {
    final data = item.toJson(); // Convert the item to a JSON object
    _client.insert('table_name', data).then((response) {
      // Handle response
    });
  }
  // ... similar implementations for update, delete, get
}
```

## Related Documents

- [[30-All-Notes/Create_generic_repository_Flutter.md]]
