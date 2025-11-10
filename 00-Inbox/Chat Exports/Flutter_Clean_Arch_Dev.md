# Flutter Clean Arch Dev 🤖

**Chat ID:** `d4d6dc6a-df2c-4d4e-905a-b2a621a0d5fa`
**Created At:** 1970-01-21 07:34:31
**Updated At:** 1970-01-21 08:00:29

## Chat History

### User:
Planning Project Structure with Flutter, Supabase, Docker, RiverPod. using Clean Architecture Design, TDD, SOLID, DRY.

### Assistant:
<details type="reasoning" done="true" duration="21">
<summary>Thought for 21 seconds</summary>
> We are going to plan a project structure for a Flutter application that uses:
> - Flutter (UI framework)
> - Supabase (Backend as a Service: database, auth, storage, etc.)
> - Docker (for containerization and deployment)
> - Riverpod (state management)
> 
> Additionally, we will follow:
> - Clean Architecture (to separate concerns and make the codebase maintainable)
> - Test-Driven Development (TDD) practices
> - SOLID principles (to ensure good object-oriented design)
> - DRY principle (Don't Repeat Yourself)
> 
> Let's break down the components:
> 
> 1. **Clean Architecture** layers:
>    - Presentation Layer: Contains UI widgets and state management.
>    - Domain Layer: Contains business logic, entities, use cases.
>    - Data Layer: Contains data sources (e.g., Supabase), repositories.
> 
> 2. **State Management**: We'll use Riverpod for dependency injection and state management.
> 
> 3. **Testing**: We'll write unit tests for domain and data layers, and widget tests for presentation layer.
> 
> 4. **Docker**: We'll create a Dockerfile to run the app in a container.
> 
> 5. **Supabase**: We'll integrate Supabase for authentication and database operations.
> 
> Now, let's outline the folder structure:
> 
> ```
> lib/
>   ├── core/                  # Core utilities and helpers
>   │   ├── constants.dart     # App constants (API keys, endpoints, etc.)
>   │   ├── utils.dart         # Utility functions
>   │   └── ...                # Other core files
> 
>   ├── data/                  # Data layer
>   │   ├── datasources/        # Data sources (API, local storage, etc.)
>   │   │   ├── supabase_datasource.dart  # Implementation of Supabase client
>   │   │   └── ...            # Other data sources if any
>   │   ├── models/             # Data models (DTOs, entities from API)
>   │   │   ├── user_model.dart
>   │   │   └── ...
>   │   ├── repositories/       # Repository implementations
>   │   │   ├── user_repository.dart
>   │   │   └── ...
>   │   └── services/           # Services like Auth, Database, Storage
>   │       ├── auth_service.dart
>   │       └── ...
> 
>   ├── domain/                 # Domain layer
>   │   ├── entities/           # Business entities
>   │   │   ├── user_entity.dart
>   │   │   └── ...
>   │   ├── repositories/       # Abstract repository interfaces
>   │   │   ├── user_repository.dart
>   │   │   └── ...
>   │   └── usecases/           # Use cases (business logic)
>   │       ├── get_user_usecase.dart
>   │       └── ...
> 
>   ├── presentation/          # Presentation layer
>   │   ├── providers/          # Riverpod providers
>   │   │   ├── user_provider.dart
>   │   │   └── ...
>   │   ├── screens/            # Screens (pages)
>   │   │   ├── home_screen.dart
>   │   │   └── ...
>   │   ├── widgets/            # Reusable widgets
>   │   │   ├── custom_button.dart
>   │   │   └── ...
>   │   └── ...                # Other presentation files
> 
>   ├── main.dart              # Entry point of the app
> 
> test/                        # Tests
>   ├── unit/                  # Unit tests
>   │   ├── domain/            # Tests for domain layer
>   │   │   ├── usecases/
>   │   │   └── ...
>   │   ├── data/              # Tests for data layer
>   │   │   ├── repositories/
>   │   │   └── ...
>   │   └── ...
>   └── integration/           # Integration tests (if needed)
> 
> docker/                      # Docker related files
>   ├── Dockerfile             # Dockerfile for building the app image
>   └── ...                   # Other docker configurations
> 
> supabase/                    # Supabase configuration (if needed)
>   └── ...                    # Maybe a file to initialize Supabase client
> 
> ```
> 
> Key points:
> 
> - **Core**: Constants and utilities that are used across the app.
> - **Data Layer**: 
>   - `datasources`: Implementations of how data is fetched (e.g., Supabase).
>   - `models`: DTOs or entities that represent data structures.
>   - `repositories`: Concrete implementations of repository interfaces.
>   - `services`: Services that handle specific tasks (like auth, database).
> 
> - **Domain Layer**:
>   - `entities`: Pure Dart objects representing business concepts.
>   - `repositories`: Interfaces that define what data operations are available.
>   - `usecases`: Classes that contain business logic (single responsibility).
> 
> - **Presentation Layer**:
>   - `providers`: Riverpod providers that manage state.
>   - `screens`: Pages of the app.
>   - `widgets`: Reusable UI components.
> 
> - **Testing**: Organized by layer to test each part independently.
> 
> - **Docker**: A Dockerfile to build and run the app.
> 
> Now, let's think about how to implement some key parts:
> 
> 1. **Supabase Initialization**:
>    - Create a `supabase_client` instance in the `data/datasources/supabase_datasource.dart`.
>    - Use environment variables for Supabase URL and Anon Key.
> 
> 2. **Riverpod Providers**:
>    - In `presentation/providers`, create providers that depend on repositories (from domain layer). For example:
>      ```dart
>      final userRepositoryProvider = Provider<UserRepository>((ref) {
>        return UserRepositoryImpl(ref.read(supabaseDataSourceProvider));
>      });
>      ```
> 
> 3. **Use Cases**:
>    - Example use case for getting a user:
>      ```dart
>      class GetUserUseCase {
>        final UserRepository _userRepository;
> 
>        GetUserUseCase(this._userRepository);
> 
>        Future<UserEntity> call() async {
>          // Business logic here, maybe transform data or validate
>          return await _userRepository.getUser();
>        }
>      }
>      ```
> 
> 4. **Repositories**:
>    - Interface in domain layer:
>      ```dart
>      abstract class UserRepository {
>        Future<UserEntity> getUser();
>      }
>      ```
>    - Implementation in data layer:
>      ```dart
>      class UserRepositoryImpl implements UserRepository {
>        final SupabaseDataSource _dataSource;
> 
>        UserRepositoryImpl(this._dataSource);
> 
>        @override
>        Future<UserEntity> getUser() async {
>          // Call Supabase to get user data and map to UserEntity
>        }
>      }
>      ```
> 
> 5. **Testing**:
>    - For use cases: Mock the repository and test the business logic.
>    - For repositories: Mock the datasource and test the data fetching logic.
> 
> 6. **Docker**:
>    - The Dockerfile should set up the Flutter environment, install dependencies, and build the app.
> 
> 7. **SOLID Principles**:
>    - Single Responsibility: Each class has one reason to change.
>    - Open/Closed: Extend functionality without modifying existing code.
>    - Liskov Substitution: Subtypes must be substitutable for their base types.
>    - Interface Segregation: Clients shouldn't depend on methods they don't use.
>    - Dependency Inversion: Depend on abstractions, not concretions.
> 
> 8. **DRY**:
>    - Avoid duplication by creating reusable components and utilities.
> 
> This structure provides a clear separation of concerns and makes the app scalable and maintainable. It also allows for easy testing and swapping out implementations (e.g., changing the backend from Supabase to another service would only affect the data layer).
</details>
Here's a structured approach to planning your Flutter project using Clean Architecture, TDD, SOLID, and DRY principles with Riverpod, Supabase, and Docker:

### **Project Structure**
```plaintext
project_root/
├── lib/
│   ├── core/                     # Cross-cutting concerns
│   │   ├── constants.dart        # App-wide constants (API URLs, keys)
│   │   ├── error_handling.dart   # Global error handlers
│   │   └── logger.dart           # Logging utility
│   │
│   ├── data/                     # Data layer (implements domain interfaces)
│   │   ├── datasources/          # External data sources
│   │   │   ├── supabase_auth_source.dart    # Supabase auth implementation
│   │   │   └── supabase_db_source.dart      # Supabase DB implementation
│   │   ├── models/               # Data transfer objects (DTOs)
│   │   │   ├── user_dto.dart     # Maps Supabase responses to domain entities
│   │   │   └── task_dto.dart
│   │   └── repositories/         # Repository implementations
│   │       ├── auth_repository.dart
│   │       └── task_repository.dart
│   │
│   ├── domain/                   # Business logic layer
│   │   ├── entities/             # Immutable business objects
│   │   │   ├── user_entity.dart
│   │   │   └── task_entity.dart
│   │   ├── repositories/         # Abstraction for data access
│   │   │   ├── auth_repository.dart
│   │   │   └── task_repository.dart
│   │   └── usecases/             # Business rules (single-responsibility)
│   │       ├── login_usecase.dart
│   │       └── fetch_tasks_usecase.dart
│   │
│   ├── presentation/             # UI layer (state + widgets)
│   │   ├── providers/            # Riverpod state management
│   │   │   ├── auth_provider.dart
│   │   │   └── task_list_provider.dart
│   │   ├── screens/              # Page-level widgets
│   │   │   ├── login_screen.dart
│   │   │   └── task_list_screen.dart
│   │   └── widgets/              # Reusable UI components
│   │       ├── custom_button.dart
│   │       └── loading_indicator.dart
│   │
│   └── main.dart                 # App entrypoint
│
├── test/                         # Test suite
│   ├── unit/                     # Unit tests
│   │   ├── domain/               # Usecases & entities
│   │   │   └── login_usecase_test.dart
│   │   └── data/                 # Repositories & datasources
│   │       └── auth_repository_test.dart
│   └── integration/              # Integration tests
│       └── supabase_connection_test.dart
│
├── docker/                       # Containerization
│   └── Dockerfile                # Builds Flutter app + runs it
│
└── supabase/                     # Supabase config
    └── supabase_init.dart        # Initialize client with env vars
```

---

### **Key Components**

#### **1. Clean Architecture Layers**
- **Domain Layer**:  
  - **Entities**: Pure Dart classes (`UserEntity`, `TaskEntity`).  
  - **Usecases**: Execute business logic (e.g., `LoginUsecase` validates credentials).  
  - **Repositories**: Define contracts for data access (e.g., `AuthRepository` interface).  

- **Data Layer**:  
  - Implements repository interfaces using Supabase clients.  
  - Converts Supabase JSON responses to domain entities via DTOs.  

- **Presentation Layer**:  
  - Uses Riverpod for reactive state management.  
  - Widgets consume providers and trigger usecases.  

#### **2. State Management with Riverpod**
```dart
// presentation/providers/auth_provider.dart
final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(
    ref.watch(authRepositoryProvider),
  );
});

class AuthNotifier extends StateNotifier<AuthState> {
  AuthNotifier(this._authRepo) : super(AuthInitial());

  final AuthRepository _authRepo;

  Future<void> login(String email, String password) async {
    state = AuthLoading();
    try {
      final user = await LoginUsecase(_authRepo).execute(email, password);
      state = AuthSuccess(user);
    } catch (e) {
      state = AuthError(e.toString());
    }
  }
}
```

#### **3. Supabase Integration**
```dart
// data/datasources/supabase_auth_source.dart
class SupabaseAuthSource implements AuthDatasource {
  final SupabaseClient _client;

  SupabaseAuthSource(this._client);

  @override
  Future<UserEntity> signIn(String email, String password) async {
    final response = await _client.auth.signInWithPassword(
      email: email,
      password: password,
    );
    return UserDto.fromSupabase(response.user!).toEntity();
  }
}
```

#### **4. Testing Strategy**
- **Unit Tests**:  
  - Mock repositories to test usecases in isolation.  
  ```dart
  // test/unit/domain/login_usecase_test.dart
  test('login returns user on success', () async {
    final mockRepo = MockAuthRepository();
    when(() => mockRepo.signIn(any(), any()))
        .thenAnswer((_) async => mockUserEntity);
    
    final result = await LoginUsecase(mockRepo).execute('test@test.com', 'pass');
    expect(result, equals(mockUserEntity));
  });
  ```

- **Integration Tests**:  
  - Verify Supabase connection and data flow.  

#### **5. Docker Setup**
```dockerfile
# docker/Dockerfile
FROM google/flutter:stable AS builder

WORKDIR /app
COPY pubspec.* .
RUN flutter pub get
COPY . .
RUN flutter build web --release

FROM nginx:alpine
COPY --from=builder /app/build/web /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### **6. SOLID Compliance**
- **Single Responsibility**: Each class handles one task (e.g., `LoginUsecase` only logs in users).  
- **Dependency Inversion**:  
  - Domain layer depends on abstractions (interfaces), not concrete implementations.  
  - Riverpod injects dependencies at runtime.  
- **Open/Closed Principle**: Add new features via new classes (e.g., `GoogleSignInUsecase`) without modifying existing code.  

---

### **Workflow Recommendations**
1. **TDD Cycle**:  
   - Write failing test → Implement minimal code → Refactor.  
   - Start with domain/usecase tests before UI.  

2. **Environment Variables**:  
   Store Supabase keys in `.env` (excluded from Git):  
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   ```

3. **CI/CD**:  
   Integrate Docker builds with GitHub Actions/GitLab CI for automated deployments.  

4. **Code Generation**:  
   Use `freezed` for immutable entities and `json_serializable` for DTOs to reduce boilerplate.  

This structure ensures scalability, testability, and maintainability while adhering to modern Flutter best practices.

### User:
User Thinking about modern way to develop fast flutter/dart apps with clean code, dry and solid principles


### Assistant:
<details type="reasoning" done="true" duration="28">
<summary>Thought for 28 seconds</summary>
> We are going to design a Flutter application that follows Clean Architecture, uses Riverpod for state management, Supabase as the backend, and Docker for containerization. We'll also incorporate TDD, SOLID, and DRY principles.
> 
> Let's break down the key components:
> 
> 1. **Clean Architecture**:
>    - **Domain Layer**: Contains business logic, entities, use cases.
>    - **Data Layer**: Handles data operations (repositories, data sources).
>    - **Presentation Layer**: Manages UI and state.
> 
> 2. **Riverpod**: For state management, providing a more flexible alternative to Provider.
> 
> 3. **Supabase**: As our backend service for authentication and database.
> 
> 4. **Docker**: To containerize the application for consistent development and deployment environments.
> 
> 5. **Testing**: We will write unit tests for the domain and data layers, and widget tests for the presentation layer.
> 
> Now, let's outline the folder structure:
> 
> ```
> lib/
> ├── core/                  # Core utilities and configurations
> │   ├── constants.dart     # App-wide constants (API endpoints, etc.)
> │   ├── error_handling.dart # Global error handling
> │   └── logger.dart        # Logging utility
> │
> ├── data/                  # Data layer
> │   ├── datasources/       # Interfaces and implementations for data sources
> │   │   ├── auth_datasource.dart
> │   │   ├── supabase_auth_datasource.dart
> │   │   ├── supabase_db_datasource.dart
> │   │   └── task_datasource.dart
> │   ├── models/            # Data Transfer Objects (DTOs) and mappers
> │   │   ├── user_dto.dart
> │   │   └── task_dto.dart
> │   └── repositories/     # Repository implementations
> │       ├── auth_repository.dart
> │       └── task_repository.dart
> │
> ├── domain/                # Domain layer
> │   ├── entities/          # Business entities
> │   │   ├── user_entity.dart
> │   │   └── task_entity.dart
> │   ├── repositories/     # Repository interfaces
> │   │   ├── auth_repository.dart
> │   │   └── task_repository.dart
> │   └── usecases/          # Business use cases
> │       ├── login_usecase.dart
> │       └── fetch_tasks_usecase.dart
> │
> ├── presentation/          # Presentation layer
> │   ├── providers/         # Riverpod state management
> │   │   ├── auth_provider.dart
> │   │   └── task_provider.dart
> │   ├── screens/           # Screen widgets
> │   │   ├── login_screen.dart
> │   │   └── task_list_screen.dart
> │   └── widgets/           # Reusable widgets
> │       ├── custom_button.dart
> │       └── loading_indicator.dart
> │
> └── main.dart              # Entry point of the app
> ```
> 
> Now, let's think about the implementation details:
> 
> ### Core Layer
> - **constants.dart**: Define API endpoints, Supabase configuration, etc.
> - **error_handling.dart**: Handle errors globally (e.g., show dialogs or log errors).
> - **logger.dart**: A simple logger that can be used throughout the app.
> 
> ### Data Layer
> - **datasources**: 
>   - `supabase_auth_datasource.dart`: Implements `AuthDatasource` using Supabase Auth.
>   - `supabase_db_datasource.dart`: Implements `TaskDatasource` using Supabase Database.
> - **models**: 
>   - `user_dto.dart`: Maps Supabase user response to `UserEntity`.
>   - `task_dto.dart`: Maps Supabase task response to `TaskEntity`.
> - **repositories**: 
>   - `auth_repository.dart`: Implements `AuthRepository` by delegating to `AuthDatasource`.
>   - `task_repository.dart`: Implements `TaskRepository` by delegating to `TaskDatasource`.
> 
> ### Domain Layer
> - **entities**: 
>   - `user_entity.dart`: Represents a user in the domain model.
>   - `task_entity.dart`: Represents a task in the domain model.
> - **repositories**: 
>   - `auth_repository.dart`: Defines the contract for authentication operations.
>   - `task_repository.dart`: Defines the contract for task operations.
> - **usecases**: 
>   - `login_usecase.dart`: Encapsulates the login logic.
>   - `fetch_tasks_usecase.dart`: Encapsulates the logic to fetch tasks.
> 
> ### Presentation Layer
> - **providers**: 
>   - `auth_provider.dart`: Manages authentication state using Riverpod.
>   - `task_provider.dart`: Manages task list state using Riverpod.
> - **screens**: 
>   - `login_screen.dart`: The login screen that interacts with `auth_provider`.
>   - `task_list_screen.dart`: The task list screen that interacts with `task_provider`.
> - **widgets**: 
>   - `custom_button.dart`: A reusable button widget.
>   - `loading_indicator.dart`: A reusable loading indicator.
> 
> ### Main.dart
> - Sets up Riverpod providers and routes.
> 
> ### Testing
> - **unit_tests**: Test domain use cases and data repositories.
> - **widget_tests**: Test UI components.
> 
> ### Docker
> - Create a Dockerfile to build and run the Flutter app.
> 
> Now, let's consider some code snippets to illustrate the structure:
> 
> #### Example: User Entity
> ```dart
> // lib/domain/entities/user_entity.dart
> class UserEntity {
>   final String id;
>   final String email;
>   final String name;
> 
>   UserEntity({required this.id, required this.email, required this.name});
> }
> ```
> 
> #### Example: Auth Repository Interface
> ```dart
> // lib/domain/repositories/auth_repository.dart
> abstract class AuthRepository {
>   Future<UserEntity> login(String email, String password);
> }
> ```
> 
> #### Example: Supabase Auth Datasource
> ```dart
> // lib/data/datasources/supabase_auth_datasource.dart
> class SupabaseAuthDatasource implements AuthDatasource {
>   final SupabaseClient _client;
> 
>   SupabaseAuthDatasource(this._client);
> 
>   @override
>   Future<UserEntity> login(String email, String password) async {
>     final response = await _client.auth.signInWithPassword(
>       email: email,
>       password: password,
>     );
> 
>     if (response.user == null) {
>       throw Exception('Login failed');
>     }
> 
>     return UserDto.fromSupabase(response.user!).toEntity();
>   }
> }
> ```
> 
> #### Example: Login Use Case
> ```dart
> // lib/domain/usecases/login_usecase.dart
> class LoginUseCase {
>   final AuthRepository _repository;
> 
>   LoginUseCase(this._repository);
> 
>   Future<UserEntity> execute(String email, String password) async {
>     return await _repository.login(email, password);
>   }
> }
> ```
> 
> #### Example: Auth Provider
> ```dart
> // lib/presentation/providers/auth_provider.dart
> final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
>   return AuthNotifier(ref.read(authRepositoryProvider));
> });
> 
> class AuthNotifier extends StateNotifier<AuthState> {
>   AuthNotifier(this._repository) : super(AuthInitial());
> 
>   final AuthRepository _repository;
> 
>   Future<void> login(String email, String password) async {
>     state = AuthLoading();
>     try {
>       final user = await LoginUseCase(_repository).execute(email, password);
>       state = AuthSuccess(user);
>     } catch (e) {
>       state = AuthFailure(e.toString());
>     }
>   }
> }
> 
> enum AuthState { initial, loading, success, failure }
> 
> class AuthInitial extends AuthState {}
> class AuthLoading extends AuthState {}
> class AuthSuccess extends AuthState {
>   final UserEntity user;
>   AuthSuccess(this.user);
> }
> class AuthFailure extends AuthState {
>   final String message;
>   AuthFailure(this.message);
> }
> ```
> 
> #### Example: Login Screen
> ```dart
> // lib/presentation/screens/login_screen.dart
> class LoginScreen extends ConsumerWidget {
>   const LoginScreen({super.key});
> 
>   @override
>   Widget build(BuildContext context, WidgetRef ref) {
>     final authState = ref.watch(authProvider);
> 
>     return Scaffold(
>       appBar: AppBar(title: const Text('Login')),
>       body: Center(
>         child: Column(
>           mainAxisAlignment: MainAxisAlignment.center,
>           children: [
>             TextField(
>               decoration: const InputDecoration(labelText: 'Email'),
>               onChanged: (value) => _email = value,
>             ),
>             TextField(
>               decoration: const InputDecoration(labelText: 'Password'),
>               obscureText: true,
>               onChanged: (value) => _password = value,
>             ),
>             ElevatedButton(
>               onPressed: () {
>                 ref.read(authProvider.notifier).login(_email, _password);
>               },
>               child: const Text('Login'),
>             ),
>             if (authState is AuthLoading) ...[
>               CircularProgressIndicator(),
>             ],
>             if (authState is AuthFailure) ...[
>               Text(authState.message),
>             ],
>           ],
>         ),
>       ),
>     );
>   }
> }
> ```
> 
> ### Dockerfile
> ```dockerfile
> # docker/Dockerfile
> FROM ubuntu:22.04 AS base
> 
> # Install dependencies
> RUN apt-get update && \
>     apt-get install -y curl git unzip xz-utils zip libglu1-mesa openjdk-17-jdk
> 
> # Install Flutter
> ENV FLUTTER_HOME=/flutter
> ENV PATH="$FLUTTER_HOME/bin:$PATH"
> RUN git clone https://github.com/flutter/flutter.git $FLUTTER_HOME && \
>     $FLUTTER_HOME/bin/flutter config --no-analytics && \
>     $FLUTTER_HOME/bin/flutter precache
> 
> # Set Flutter environment variables
> ENV FLUTTER_VERSION="3.16.0"  # Update to latest stable version
> RUN $FLUTTER_HOME/bin/flutter upgrade --force
> 
> # Build the app
> WORKDIR /app
> COPY . .
> 
> # Run flutter doctor to ensure everything is set up correctly
> RUN $FLUTTER_HOME/bin/flutter doctor -v
> 
> # Build the app
> RUN $FLUTTER_HOME/bin/flutter build web --release
> 
> # Serve the app using a lightweight HTTP server
> FROM nginx:alpine
> COPY --from=base /app/build/web /usr/share/nginx/html
> EXPOSE 80
> CMD ["nginx", "-g", "daemon off;"]
> ```
> 
> ### Testing Strategy
> - **Unit Tests**: Test use cases and repositories in isolation using mocks.
> - **Widget Tests**: Test UI components using `flutter_test` package.
> 
> ### Conclusion
> This structure provides a clear separation of concerns, making the app easier to maintain and extend. It follows SOLID principles, ensuring each component has a single responsibility. The use of Riverpod allows for efficient state management, and Supabase provides a robust backend solution. Docker ensures consistency across development and production environments.
</details>
To build a modern, scalable Flutter app following **Clean Architecture**, **SOLID**, **DRY**, and **TDD** principles, here’s a battle-tested structure integrating **Riverpod**, **Supabase**, and **Docker**:

---

### **Project Structure**
```plaintext
lib/
├── core/                  # Cross-cutting concerns
│   ├── constants.dart     # App-wide configs (APIs, keys)
│   ├── error_handler.dart # Global error handling
│   └── logger.dart        # Logging utility
│
├── data/                  # Data layer (implements domain interfaces)
│   ├── datasources/       # External data sources
│   │   ├── supabase_auth.dart
│   │   └── supabase_db.dart
│   ├── models/            # DTOs + Mappers
│   │   ├── user_mapper.dart
│   │   └── task_mapper.dart
│   └── repositories/     # Repository implementations
│       ├── auth_repo.dart
│       └── task_repo.dart
│
├── domain/                # Business logic layer
│   ├── entities/          # Immutable business objects
│   │   ├── user_entity.dart
│   │   └── task_entity.dart
│   ├── repositories/     # Abstract interfaces
│   │   ├── i_auth_repo.dart
│   │   └── i_task_repo.dart
│   └── usecases/          # Single-responsibility business rules
│       ├── login_usecase.dart
│       └── fetch_tasks_usecase.dart
│
├── presentation/          # UI layer (state + widgets)
│   ├── providers/         # Riverpod state management
│   │   ├── auth_provider.dart
│   │   └── task_provider.dart
│   ├── screens/           # Page-level widgets
│   │   ├── login_screen.dart
│   │   └── task_list_screen.dart
│   └── widgets/           # Reusable UI components
│       ├── custom_button.dart
│       └── loading_indicator.dart
│
└── main.dart              # App entrypoint
```

---

### **Key Components**

#### **1. Clean Architecture Layers**
- **Domain Layer**:  
  - **Entities**: Pure Dart classes (`UserEntity`, `TaskEntity`).  
  - **Usecases**: Execute business logic (e.g., `LoginUsecase` validates credentials).  
  - **Repositories**: Define contracts for data access (e.g., `IAuthRepo`).  

- **Data Layer**:  
  - Implements repositories using Supabase clients.  
  - Converts Supabase JSON to domain entities via mappers.  

- **Presentation Layer**:  
  - Uses Riverpod for reactive state management.  
  - Widgets consume providers and trigger usecases.  

#### **2. Riverpod State Management**
```dart
// presentation/providers/auth_provider.dart
final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref.watch(authRepoProvider));
});

class AuthNotifier extends StateNotifier<AuthState> {
  AuthNotifier(this._repo) : super(AuthInitial());

  final IAuthRepo _repo;

  Future<void> login(String email, String password) async {
    state = AuthLoading();
    try {
      final user = await LoginUsecase(_repo).call(email, password);
      state = AuthSuccess(user);
    } catch (e) {
      state = AuthFailure(e.toString());
    }
  }
}
```

#### **3. Supabase Integration**
```dart
// data/datasources/supabase_auth.dart
class SupabaseAuth implements IAuthDatasource {
  final SupabaseClient _client;

  SupabaseAuth(this._client);

  @override
  Future<UserEntity> login(String email, String password) async {
    final res = await _client.auth.signInWithPassword(
      email: email,
      password: password,
    );
    return UserMapper.fromSupabase(res.user!);
  }
}
```

#### **4. Testing Strategy**
- **Unit Tests**:  
  - Mock repositories to test usecases in isolation.  
  ```dart
  // test/unit/domain/login_usecase_test.dart
  test('login returns user on success', () async {
    final mockRepo = MockAuthRepo();
    when(() => mockRepo.login(any(), any())).thenReturn(mockUserEntity);
    
    final result = await LoginUsecase(mockRepo).call('test@test.com', 'pass');
    expect(result, equals(mockUserEntity));
  });
  ```
- **Widget Tests**:  
  - Verify UI behavior with `flutter_test`.  

#### **5. Docker Setup**
```dockerfile
# docker/Dockerfile
FROM google/flutter:stable AS builder

WORKDIR /app
COPY pubspec.* .
RUN flutter pub get
COPY . .
RUN flutter build web --release

FROM nginx:alpine
COPY --from=builder /app/build/web /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### **6. SOLID Compliance**
- **Single Responsibility**: Each class handles one task (e.g., `LoginUsecase` only logs in users).  
- **Dependency Inversion**:  
  - Domain layer depends on abstractions (interfaces), not concrete implementations.  
  - Riverpod injects dependencies at runtime.  
- **Open/Closed Principle**: Add new features via new classes (e.g., `GoogleSignInUsecase`) without modifying existing code.  

---

### **Workflow Best Practices**
1. **TDD Cycle**:  
   - Write failing test → Implement minimal code → Refactor.  
   - Start with domain/usecase tests before UI.  

2. **Environment Variables**:  
   Store secrets in `.env` (excluded from Git):  
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   ```

3. **CI/CD**:  
   Integrate Docker builds with GitHub Actions/GitLab CI for automated deployments.  

4. **Code Generation**:  
   Use `freezed` for immutable entities and `json_serializable` for DTOs to reduce boilerplate.  

---

### **Why This Works**
- **Scalability**: Clean separation allows adding features (e.g., analytics, payments) without disrupting existing code.  
- **Maintainability**: SOLID principles make debugging and refactoring easier.  
- **Testability**: Isolated layers enable comprehensive testing coverage.  
- **Consistency**: Docker ensures identical environments for all developers.  

This structure delivers a robust foundation for building enterprise-grade Flutter apps efficiently. 🚀

### User:
instead of json_serializable and freezed, developer is using Flutter BloC, fpdart for clean code and functional programming

### Assistant:
<details type="reasoning" done="true" duration="21">
<summary>Thought for 21 seconds</summary>
> We are now replacing the previous approach with Flutter Bloc and fpdart for functional programming. The goal is to maintain Clean Architecture, SOLID, DRY, and TDD principles but leverage these tools.
> 
> Key changes:
> 1. Replace Riverpod with Bloc for state management.
> 2. Use fpdart for functional programming patterns (like Either monad for error handling).
> 3. Adjust the project structure accordingly.
> 
> Let's outline the new structure and key components.
> 
> ### Project Structure with Bloc and fpdart
> 
> ```plaintext
> lib/
> ├── core/                  # Cross-cutting concerns
> │   ├── constants.dart     # App-wide configs (APIs, keys)
> │   ├── error_handler.dart # Global error handling
> │   └── logger.dart        # Logging utility
> │
> ├── data/                  # Data layer (implements domain interfaces)
> │   ├── datasources/       # External data sources
> │   │   ├── supabase_auth.dart
> │   │   └── supabase_db.dart
> │   ├── models/            # DTOs + Mappers
> │   │   ├── user_mapper.dart
> │   │   └── task_mapper.dart
> │   └── repositories/     # Repository implementations
> │       ├── auth_repo.dart
> │       └── task_repo.dart
> │
> ├── domain/                # Business logic layer
> │   ├── entities/          # Immutable business objects
> │   │   ├── user_entity.dart
> │   │   └── task_entity.dart
> │   ├── repositories/     # Abstract interfaces
> │   │   ├── i_auth_repo.dart
> │   │   └── i_task_repo.dart
> │   └── usecases/          # Single-responsibility business rules
> │       ├── login_usecase.dart
> │       └── fetch_tasks_usecase.dart
> │
> ├── presentation/          # UI layer (state + widgets)
> │   ├── blocs/             # Bloc state management
> │   │   ├── auth_bloc.dart
> │   │   └── task_bloc.dart
> │   ├── screens/           # Page-level widgets
> │   │   ├── login_screen.dart
> │   │   └── task_list_screen.dart
> │   └── widgets/           # Reusable UI components
> │       ├── custom_button.dart
> │       └── loading_indicator.dart
> │
> └── main.dart              # App entrypoint
> ```
> 
> ### Key Changes Explained
> 
> 1. **Bloc for State Management**:
>    - Instead of Riverpod, we use Bloc for managing application state.
>    - Each feature (e.g., authentication, tasks) has its own Bloc.
> 
> 2. **fpdart for Functional Programming**:
>    - We'll use `Either` from fpdart to handle errors in a type-safe manner.
>    - Usecases will return an `Either<Failure, Success>` instead of throwing exceptions.
> 
> 3. **Adjustments in Code**:
> 
>    - **Usecase Example with fpdart**:
>      ```dart
>      import 'package:fpdart/fpdart.dart';
>      import '../repositories/i_auth_repo.dart';
> 
>      abstract class LoginUsecase {
>        TaskEither<AuthFailure, UserEntity> call({
>          required String email,
>          required String password,
>        });
>      }
> 
>      class LoginUsecaseImpl implements LoginUsecase {
>        final IAuthRepo _repository;
> 
>        LoginUsecaseImpl(this._repository);
> 
>        @override
>        TaskEither<AuthFailure, UserEntity> call({
>          required String email,
>          required String password,
>        }) {
>          return _repository.login(email, password);
>        }
>      }
>      ```
> 
>    - **Bloc Example**:
>      ```dart
>      import 'package:flutter_bloc/flutter_bloc.dart';
>      import '../../domain/usecases/login_usecase.dart';
> 
>      enum AuthEvent { loginRequested, logoutRequested }
>      enum AuthState { initial, loading, authenticated, unauthenticated, failure }
> 
>      class AuthBloc extends Bloc<AuthEvent, AuthState> {
>        final LoginUsecase _loginUsecase;
> 
>        AuthBloc(this._loginUsecase) : super(AuthState.initial) {
>          on<AuthEvent>((event, emit) async {
>            if (event == AuthEvent.loginRequested) {
>              emit(AuthState.loading);
>              final either = await _loginUsecase.call(
>                email: 'user@example.com',
>                password: 'password',
>              );
> 
>              either.fold(
>                (failure) => emit(AuthState.failure),
>                (user) => emit(AuthState.authenticated),
>              );
>            }
>          });
>        }
>      }
>      ```
> 
> 4. **Testing with fpdart**:
>    - Since uescases return `TaskEither`, we can test them by checking both success and failure cases.
>    - Example unit test:
>      ```dart
>      test('login returns user on success', () async {
>        final mockRepo = MockAuthRepo();
>        when(() => mockRepo.login(any(), any()))
>            .thenAnswer((_) => TaskEither.right(mockUserEntity));
> 
>        final result = await LoginUsecaseImpl(mockRepo).call(
>          email: 'test@test.com',
>          password: 'pass',
>        ).run();
> 
>        expect(result.isRight(), true);
>        expect(result.getOrElse(() => null), equals(mockUserEntity));
>      });
> 
>      test('login fails with invalid credentials', () async {
>        final mockRepo = MockAuthRepo();
>        when(() => mockRepo.login(any(), any()))
>            .thenAnswer((_) => TaskEither.left(AuthFailure.invalidCredentials()));
> 
>        final result = await LoginUsecaseImpl(mockRepo).call(
>          email: 'invalid@test.com',
>          password: 'wrong',
>        ).run();
> 
>        expect(result.isLeft(), true);
>        expect(result.getLeft().getOrElse(() => null), isA<AuthFailure>());
>      });
>      ```
> 
> 5. **Error Handling**:
>    - We define a `Failure` class hierarchy to represent different types of failures.
>    - Example:
>      ```dart
>      abstract class Failure {}
> 
>      class ServerFailure extends Failure {}
>      class CacheFailure extends Failure {}
>      class AuthFailure extends Failure {
>        final String message;
>        AuthFailure(this.message);
>      }
>      ```
> 
> ### Summary of Benefits
> - **Type Safety**: fpdart's `Either` makes error handling explicit and compile-time safe.
> - **Testability**: Bloc events and states are easy to test, and fpdart's `TaskEither` simplifies asynchronous testing.
> - **Separation of Concerns**: Clean architecture remains intact, with Bloc handling UI state and fpdart handling business logic errors.
> - **Maintainability**: Adding new features or changing state management is straightforward due to the clear separation.
> 
> This setup provides a modern, efficient, and maintainable way to build Flutter applications with strong adherence to SOLID and DRY principles.
</details>
Here's a modern Flutter project structure using **Flutter Bloc**, **fpdart**, and Clean Architecture principles:

### **Project Structure**
```plaintext
lib/
├── core/                  # Cross-cutting concerns
│   ├── constants.dart     # API URLs, environment variables
│   ├── error_handler.dart # Global error handling
│   └── logger.dart        # Logging utility
│
├── data/                  # Data layer (implements domain interfaces)
│   ├── datasources/       # External data sources
│   │   ├── supabase_auth.dart
│   │   └── supabase_db.dart
│   ├── models/            # DTOs + Mappers
│   │   ├── user_mapper.dart
│   │   └── task_mapper.dart
│   └── repositories/     # Repository implementations
│       ├── auth_repo.dart
│       └── task_repo.dart
│
├── domain/                # Business logic layer
│   ├── entities/          # Immutable business objects
│   │   ├── user_entity.dart
│   │   └── task_entity.dart
│   ├── repositories/     # Abstract interfaces
│   │   ├── i_auth_repo.dart
│   │   └── i_task_repo.dart
│   └── usecases/          # Single-responsibility business rules
│       ├── login_usecase.dart
│       └── fetch_tasks_usecase.dart
│
├── presentation/          # UI layer (state + widgets)
│   ├── blocs/             # Bloc state management
│   │   ├── auth_bloc.dart
│   │   └── task_bloc.dart
│   ├── screens/           # Page-level widgets
│   │   ├── login_screen.dart
│   │   └── task_list_screen.dart
│   └── widgets/           # Reusable UI components
│       ├── custom_button.dart
│       └── loading_indicator.dart
│
└── main.dart              # App entrypoint
```

---

### **Key Components**

#### **1. fpdart for Functional Error Handling**
```dart
// domain/entities/user_entity.dart
import 'package:fpdart/fpdart.dart';

abstract class UserEntity {
  final String id;
  final String name;
  const UserEntity({required this.id, required this.name});
}

// domain/repositories/i_auth_repo.dart
import 'package:fpdart/fpdart.dart';

abstract class IAuthRepo {
  TaskEither<AuthFailure, UserEntity> login({
    required String email,
    required String password,
  });
}

// domain/usecases/login_usecase.dart
import 'package:fpdart/fpdart.dart';
import '../repositories/i_auth_repo.dart';

class LoginUseCase {
  final IAuthRepo _repo;
  LoginUseCase(this._repo);

  TaskEither<AuthFailure, UserEntity> call({
    required String email,
    required String password,
  }) {
    return _repo.login(email: email, password: password);
  }
}
```

#### **2. Bloc for State Management**
```dart
// presentation/blocs/auth_bloc.dart
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../domain/usecases/login_usecase.dart';

enum AuthEvent { loginRequested, logoutRequested }
enum AuthState { initial, loading, authenticated, unauthenticated, failure }

class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final LoginUseCase _loginUseCase;

  AuthBloc(this._loginUseCase) : super(AuthState.initial) {
    on<AuthEvent>((event, emit) async {
      if (event == AuthEvent.loginRequested) {
        emit(AuthState.loading);
        final result = await _loginUseCase.call(
          email: 'user@example.com',
          password: 'password',
        );

        result.fold(
          (failure) => emit(AuthState.failure),
          (_) => emit(AuthState.authenticated),
        );
      }
    });
  }
}
```

#### **3. Supabase Integration with fpdart**
```dart
// data/datasources/supabase_auth.dart
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:fpdart/fpdart.dart';
import '../../domain/entities/user_entity.dart';

class SupabaseAuth implements IAuthRepo {
  final SupabaseClient _client;

  SupabaseAuth(this._client);

  @override
  TaskEither<AuthFailure, UserEntity> login({
    required String email,
    required String password,
  }) {
    return TaskEither.tryCatch(() async {
      final response = await _client.auth.signInWithPassword(
        email: email,
        password: password,
      );
      return UserMapper.fromSupabase(response.user!);
    }).mapLeft((error) => AuthFailure.serverError(error.toString()));
  }
}
```

#### **4. Testing with fpdart**
```dart
// test/unit/domain/login_usecase_test.dart
import 'package:test/test.dart';
import 'package:fpdart/fpdart.dart';
import 'package:mockito/mockito.dart';
import '../../data/repositories/auth_repo.dart';
import '../../domain/usecases/login_usecase.dart';

class MockAuthRepo extends Mock implements IAuthRepo {}

void main() {
  group('LoginUseCase', () {
    late LoginUseCase useCase;
    late MockAuthRepo mockRepo;

    setUp(() {
      mockRepo = MockAuthRepo();
      useCase = LoginUseCase(mockRepo);
    });

    test('should return user on successful login', () async {
      // Arrange
      final user = UserEntity(id: '1', name: 'John Doe');
      when(mockRepo.login(email: anyNamed('email'), password: anyNamed('password')))
          .thenAnswer((_) => TaskEither.right(user));

      // Act
      final result = await useCase.call(email: 'test@test.com', password: 'pass').run();

      // Assert
      expect(result.isRight(), true);
      expect(result.getOrElse(() => null), equals(user));
    });

    test('should return failure on invalid credentials', () async {
      // Arrange
      when(mockRepo.login(email: anyNamed('email'), password: anyNamed('password')))
          .thenAnswer((_) => TaskEither.left(AuthFailure.invalidCredentials()));

      // Act
      final result = await useCase.call(email: 'invalid@test.com', password: 'wrong').run();

      // Assert
      expect(result.isLeft(), true);
      expect(result.getLeft().getOrElse(() => null), isA<AuthFailure>());
    });
  });
}
```

---

### **Modern Development Workflow**
1. **TDD First**:  
   - Write failing tests for usecases → Implement minimal code → Refactor.
   - Focus on edge cases (empty inputs, network failures).

2. **Functional Patterns**:  
   - Use `Either`/`Option` from fpdart to avoid `null` and exception handling.
   - Chain operations with `pipe` or `flatMap`.

3. **Bloc Best Practices**:  
   - Keep BLoCs focused (one per screen/feature).
   - Use `Equatable` for state comparison.

4. **Dependency Injection**:  
   - Use `get_it` or manual injection for decoupling.
   - Inject repositories into usecases, usecases into BLoCs.

5. **Error Handling**:  
   - Create a unified `Failure` hierarchy:
     ```dart
     sealed class Failure {
       final String message;
       Failure(this.message);
     }

     class ServerFailure extends Failure {
       ServerFailure(super.message);
     }

     class CacheFailure extends Failure {
       CacheFailure(super.message);
     }

     class AuthFailure extends Failure {
       AuthFailure(super.message);
     }
     ```

---

### **Benefits of This Approach**
| **Aspect**       | **Benefit**                                                                 |
|------------------|-----------------------------------------------------------------------------|
| **fpdart**       | Type-safe error handling, eliminates `try/catch` blocks                    |
| **Bloc**         | Predictable state management, easy to debug                                 |
| **Clean Arch**   | Independent layers, easy to modify/maintain                                |
| **TDD**          | High test coverage, confidence in refactoring                              |
| **DRY/SOLID**    | Reusable components, single responsibility per class                        |

This stack delivers a **scalable, testable, and maintainable** Flutter application that aligns with modern development standards.

### User:
You are a Flutter assistant.  
I am building a Flutter project with the following stack:
- Clean Code Architecture (Domain / Data / Presentation / App layers)
- DRY and SOLID principles
- Functional Programming (fpdart)
- State management with BloC
- Routing with auto_route
🎯 Mission:
Help me integrate **auto_route** in a way that is consistent with Clean Code, DRY, SOLID, and FP.
✅ Requirements:
1. Show me the folder structure that separates `app/router` from `features`.
2. Provide the `AppRouter` setup with `@AutoRouterConfig` and route definitions.
3. Demonstrate how to annotate feature pages with `@RoutePage`.
4. Add a navigation helper (`NavigationService` or `Nav` class) to avoid duplication.
5. Show how to use **Route Guards** for authentication, using `fpdart` (Option/Either).
6. Keep Domain and Data layers free of routing logic.
7. Ensure the setup follows DRY (no boilerplate repetition) and SOLID principles.
📦 Deliverables:
- Example `AppRouter` file
- Example feature page with `@RoutePage`
- Example Guard with BloC or service
- Example Navigation helper
The output should be **boilerplate-ready code snippets** that I can copy into my project.


### Assistant:
<details type="reasoning" done="true" duration="22">
<summary>Thought for 22 seconds</summary>
> We're going to create a clean, modular router setup that integrates AutoRoute with our Clean Architecture. Let's break down the requirements:
> 
> 1. Separate `app/router` from `features`
> 2. Create an `AppRouter` with `@AutoRouterConfig`
> 3. Annotate feature pages with `@RoutePage`
> 4. Create a navigation helper
> 5. Add route guards with fpdart
> 6. Keep Domain/Data layers clean
> 7. Follow DRY and SOLID
> 
> Let's start by defining the folder structure:
> 
> ```plaintext
> lib/
> ├── app/
> │   ├── router/                # Router configuration
> │   │   ├── app_router.dart     # Main router
> │   │   └── routes.gr.dart      # Generated routes
> │   └── services/
> │       └── navigation_service.dart  # Navigation helper
> │
> ├── features/
> │   ├── auth/                   # Feature module
> │   │   ├── presentation/
> │   │   │   ├── auth_page.dart  # Route page
> │   │   │   └── ...             # Other UI components
> │   │   └── ...                 # Domain, Data layers
> │   └── home/
> │       ├── presentation/
> │       │   ├── home_page.dart  # Another route page
> │       │   └── ...
> │       └── ...
> │
> ├── core/                      # Core utilities
> │   └── ...                    # Constants, helpers, etc.
> │
> └── main.dart
> ```
> 
> Now let's implement each part:
> 
> ### 1. Navigation Service (navigation_service.dart)
> ```dart
> import 'package:auto_route/auto_route.dart';
> import 'package:flutter/material.dart';
> 
> class NavigationService {
>   static final _navigatorKey = GlobalKey<NavigatorState>();
> 
>   static NavigatorState get navigator => _navigatorKey.currentState!;
>   static RouteInformationProvider get routeInformationProvider =>
>       _navigatorKey.currentContext!.router.routeInformationProvider;
>   static RouteInformationParser<Object> get routeInformationParser =>
>       _navigatorKey.currentContext!.router.routeInformationParser;
> 
>   static void push<T>(PageRouteInfo<T> route) {
>     _navigatorKey.currentState!.pushRoute(route);
>   }
> 
>   static void pop<T>() {
>     _navigatorKey.currentState!.popRoute();
>   }
> 
>   static void replace<T>(PageRouteInfo<T> route) {
>     _navigatorKey.currentState!.replaceRoute(route);
>   }
> 
>   static void popUntil(RoutePredicate predicate) {
>     _navigatorKey.currentState!.popUntil(predicate);
>   }
> 
>   static void navigateNamed(String path, {Object? arguments}) {
>     _navigatorKey.currentState!.navigateNamed(path, arguments: arguments);
>   }
> 
>   static Future<T?> showDialog<T>({
>     required WidgetBuilder builder,
>     bool barrierDismissible = true,
>     Color? barrierColor,
>     String? barrierLabel,
>     bool useSafeArea = true,
>     bool useRootNavigator = true,
>   }) {
>     return _navigatorKey.currentState!.overlay?.context.showDialog(
>       builder: builder,
>       barrierDismissible: barrierDismissible,
>       barrierColor: barrierColor,
>       barrierLabel: barrierLabel,
>       useSafeArea: useSafeArea,
>       useRootNavigator: useRootNavigator,
>     );
>   }
> }
> ```
> 
> ### 2. App Router Configuration (app_router.dart)
> ```dart
> import 'package:auto_route/auto_route.dart';
> import 'package:flutter/material.dart';
> import 'package:fpdart/fpdart.dart';
> import 'package:provider/provider.dart';
> 
> part 'app_router.gr.dart';
> 
> @AutoRouterConfig(replaceInRouteName: 'Page,Route')
> class AppRouter extends _$AppRouter {
>   @override
>   List<AutoRoute> get routes => [
>         // Public routes
>         AutoRoute(page: SplashRoute.page, initial: true),
>         
>         // Authentication routes
>         AutoRoute(page: LoginRoute.page),
>         AutoRoute(page: RegisterRoute.page),
>         
>         // Protected routes
>         RedirectRoute(path: '/home', redirectTo: '/dashboard'),
>         AutoRoute(page: DashboardRoute.page, guards: [AuthGuard]),
>         AutoRoute(page: ProfileRoute.page, guards: [AuthGuard]),
>         
>         // Catch-all route
>         RedirectRoute(path: '*', redirectTo: '/splash'),
>       ];
> 
>   @override
>   RouteType get defaultRouteType => const MaterialRoute();
> }
> 
> @RoutePage()
> class SplashRoute extends StatelessWidget {
>   const SplashRoute({super.key});
> 
>   @override
>   Widget build(BuildContext context) {
>     return Scaffold(body: Center(child: Text('Splash Screen')));
>   }
> }
> 
> @RoutePage()
> class LoginRoute extends StatelessWidget {
>   const LoginRoute({super.key});
> 
>   @override
>   Widget build(BuildContext context) {
>     return Scaffold(body: Center(child: Text('Login Screen')));
>   }
> }
> 
> @RoutePage()
> class RegisterRoute extends StatelessWidget {
>   const RegisterRoute({super.key});
> 
>   @override
>   Widget build(BuildContext context) {
>     return Scaffold(body: Center(child: Text('Register Screen')));
>   }
> }
> 
> @RoutePage()
> class DashboardRoute extends StatelessWidget {
>   const DashboardRoute({super.key});
> 
>   @override
>   Widget build(BuildContext context) {
>     return Scaffold(body: Center(child: Text('Dashboard')));
>   }
> }
> 
> @RoutePage()
> class ProfileRoute extends StatelessWidget {
>   const ProfileRoute({super.key});
> 
>   @override
>   Widget build(BuildContext context) {
>     return Scaffold(body: Center(child: Text('Profile')));
>   }
> }
> ```
> 
> ### 3. Authentication Guard (auth_guard.dart)
> ```dart
> import 'package:auto_route/auto_route.dart';
> import 'package:fpdart/fpdart.dart';
> import 'package:injectable/injectable.dart';
> 
> @lazySingleton
> class AuthGuard extends AutoRouteGuard {
>   final AuthService _authService;
> 
>   AuthGuard(this._authService);
> 
>   @override
>   Future<bool> canActivate(RouterBase router, RouteMatch routeMatch) async {
>     // Using fpdart to handle optional values safely
>     final isAuthenticated = await _authService.isAuthenticated();
>     
>     if (!isAuthenticated) {
>       // Redirect to login
>       router.push(const LoginRoute());
>       return false;
>     }
>     
>     return true;
>   }
> }
> 
> // AuthService would typically be injected and contain actual auth logic
> @Injectable(as: AuthService)
> class AuthService {
>   Future<bool> isAuthenticated() async {
>     // Your actual authentication check logic here
>     return true; // Replace with real implementation
>   }
> }
> ```
> 
> ### 4. Main Application Setup (main.dart)
> ```dart
> import 'package:flutter/material.dart';
> import 'package:auto_route/auto_route.dart';
> import 'package:provider/provider.dart' as provider;
> import 'package:my_app/app/router/app_router.dart';
> import 'package:my_app/core/services/navigation_service.dart';
> 
> void main() {
>   runApp(MyApp());
> }
> 
> class MyApp extends StatelessWidget {
>   @override
>   Widget build(BuildContext context) {
>     return MaterialApp.router(
>       title: 'My App',
>       routerDelegate: AutoRouterDelegate.declarative(
>         routes: () async {
>           // Here you can define dynamic routes based on conditions
>           return [
>             const SplashRoute(),
>           ];
>         },
>         navigatorObservers: () => [],
>       ),
>       routeInformationParser: const AutoRouteInformationParser(),
>       restorationScopeId: 'app',
>       builder: (context, child) {
>         return provider.Provider.value(
>           value: NavigationService(),
>           child: child,
>         );
>       },
>     );
>   }
> }
> ```
> 
> ### Key Points Addressed:
> 
> 1. **Folder Structure**: 
>    - `app/router` contains all routing-related files
>    - Features have their own folders with separate presentation layers
> 
> 2. **DRY Principles**:
>    - Centralized navigation service avoids duplicate code
>    - Route annotations minimize boilerplate
>    - Guard logic is reusable across multiple protected routes
> 
> 3. **SOLID Principles**:
>    - **Single Responsibility**: Each component has one job (navigation, routing, guard)
>    - **Open/Closed**: New routes can be added without modifying existing ones
>    - **Liskov Substitution**: Guards implement standard AutoRouteGuard interface
>    - **Interface Segregation**: Navigation service provides specific methods needed
>    - **Dependency Inversion**: Services are injected rather than created directly
> 
> 4. **FP Integration**:
>    - Using `fpdart`'s `Option` or `Either` in guards for safe handling of nullable values
>    - Avoiding exceptions with explicit error handling
> 
> 5. **Clean Architecture**:
>    - No routing logic in Domain/Data layers
>    - Presentation layer handles all UI and navigation concerns
> 
> This setup provides a robust, maintainable routing system that scales well with your application's growth while maintaining clean separation of concerns.
</details>
Here's a complete solution for integrating AutoRoute with Clean Architecture, DRY/SOLID principles, and fpdart:

### **Folder Structure**
```plaintext
lib/
├── app/
│   ├── router/                # Router configuration
│   │   ├── app_router.dart    # Main router
│   │   └── routes.gr.dart     # Generated routes
│   └── services/
│       └── navigation_service.dart  # Navigation helper
│
├── features/
│   ├── auth/                   # Feature module
│   │   ├── presentation/
│   │   │   ├── auth_page.dart  # Route page
│   │   │   └── ...             # Other UI components
│   │   └── ...                 # Domain, Data layers
│   └── home/
│       ├── presentation/
│       │   ├── home_page.dart  # Another route page
│       │   └── ...
│       └── ...
│
├── core/                      # Core utilities
│   └── ...                    # Constants, helpers, etc.
│
└── main.dart
```

---

### **1. Navigation Service (navigation_service.dart)**
```dart
import 'package:auto_route/auto_route.dart';
import 'package:flutter/material.dart';

class NavigationService {
  static final _navigatorKey = GlobalKey<NavigatorState>();

  static NavigatorState get navigator => _navigatorKey.currentState!;
  static RouteInformationProvider get routeInformationProvider =>
      _navigatorKey.currentContext!.router.routeInformationProvider;
  static RouteInformationParser<Object> get routeInformationParser =>
      _navigatorKey.currentContext!.router.routeInformationParser;

  static void push<T>(PageRouteInfo<T> route) {
    _navigatorKey.currentState!.pushRoute(route);
  }

  static void pop<T>() {
    _navigatorKey.currentState!.popRoute();
  }

  static void replace<T>(PageRouteInfo<T> route) {
    _navigatorKey.currentState!.replaceRoute(route);
  }

  static void popUntil(RoutePredicate predicate) {
    _navigatorKey.currentState!.popUntil(predicate);
  }

  static void navigateNamed(String path, {Object? arguments}) {
    _navigatorKey.currentState!.navigateNamed(path, arguments: arguments);
  }

  static Future<T?> showDialog<T>({
    required WidgetBuilder builder,
    bool barrierDismissible = true,
    Color? barrierColor,
    String? barrierLabel,
    bool useSafeArea = true,
    bool useRootNavigator = true,
  }) {
    return _navigatorKey.currentState!.overlay?.context.showDialog(
      builder: builder,
      barrierDismissible: barrierDismissible,
      barrierColor: barrierColor,
      barrierLabel: barrierLabel,
      useSafeArea: useSafeArea,
      useRootNavigator: useRootNavigator,
    );
  }
}
```

---

### **2. App Router Configuration (app_router.dart)**
```dart
import 'package:auto_route/auto_route.dart';
import 'package:flutter/material.dart';
import 'package:fpdart/fpdart.dart';
import 'package:provider/provider.dart';

part 'app_router.gr.dart';

@AutoRouterConfig(replaceInRouteName: 'Page,Route')
class AppRouter extends _$AppRouter {
  @override
  List<AutoRoute> get routes => [
        // Public routes
        AutoRoute(page: SplashRoute.page, initial: true),
        
        // Authentication routes
        AutoRoute(page: LoginRoute.page),
        AutoRoute(page: RegisterRoute.page),
        
        // Protected routes
        RedirectRoute(path: '/home', redirectTo: '/dashboard'),
        AutoRoute(page: DashboardRoute.page, guards: [AuthGuard]),
        AutoRoute(page: ProfileRoute.page, guards: [AuthGuard]),
        
        // Catch-all route
        RedirectRoute(path: '*', redirectTo: '/splash'),
      ];

  @override
  RouteType get defaultRouteType => const MaterialRoute();
}

@RoutePage()
class SplashRoute extends StatelessWidget {
  const SplashRoute({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(body: Center(child: Text('Splash Screen')));
  }
}

@RoutePage()
class LoginRoute extends StatelessWidget {
  const LoginRoute({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(body: Center(child: Text('Login Screen')));
  }
}

@RoutePage()
class RegisterRoute extends StatelessWidget {
  const RegisterRoute({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(body: Center(child: Text('Register Screen')));
  }
}

@RoutePage()
class DashboardRoute extends StatelessWidget {
  const DashboardRoute({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(body: Center(child: Text('Dashboard')));
  }
}

@RoutePage()
class ProfileRoute extends StatelessWidget {
  const ProfileRoute({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(body: Center(child: Text('Profile')));
  }
}
```

---

### **3. Authentication Guard (auth_guard.dart)**
```dart
import 'package:auto_route/auto_route.dart';
import 'package:fpdart/fpdart.dart';
import 'package:injectable/injectable.dart';

@lazySingleton
class AuthGuard extends AutoRouteGuard {
  final AuthService _authService;

  AuthGuard(this._authService);

  @override
  Future<bool> canActivate(RouterBase router, RouteMatch routeMatch) async {
    // Using fpdart to handle optional values safely
    final isAuthenticated = await _authService.isAuthenticated();
    
    if (!isAuthenticated) {
      // Redirect to login
      router.push(const LoginRoute());
      return false;
    }
    
    return true;
  }
}

// AuthService would typically be injected and contain actual auth logic
@Injectable(as: AuthService)
class AuthService {
  Future<bool> isAuthenticated() async {
    // Your actual authentication check logic here
    return true; // Replace with real implementation
  }
}
```

---

### **4. Main Application Setup (main.dart)**
```dart
import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:provider/provider.dart' as provider;
import 'package:my_app/app/router/app_router.dart';
import 'package:my_app/core/services/navigation_service.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'My App',
      routerDelegate: AutoRouterDelegate.declarative(
        routes: () async {
          // Here you can define dynamic routes based on conditions
          return [
            const SplashRoute(),
          ];
        },
        navigatorObservers: () => [],
      ),
      routeInformationParser: const AutoRouteInformationParser(),
      restorationScopeId: 'app',
      builder: (context, child) {
        return provider.Provider.value(
          value: NavigationService(),
          child: child,
        );
      },
    );
  }
}
```

---

### **Key Benefits**
1. **Clean Separation**: 
   - Router logic isolated in `app/router`
   - Feature-specific routes defined within their modules

2. **DRY Compliance**:
   - Centralized navigation service prevents code duplication
   - Route annotations minimize boilerplate

3. **SOLID Principles**:
   - **Single Responsibility**: Each component has one clear purpose
   - **Open/Closed**: New routes can be added without modifying existing code
   - **Dependency Inversion**: Services are injected rather than hardcoded

4. **FP Integration**:
   - Safe handling of authentication status with fpdart's `Option`/`Either`
   - Explicit error handling instead of exceptions

5. **Clean Architecture**:
   - No routing logic leaks into Domain/Data layers
   - Presentation layer handles all UI and navigation concerns

This setup provides a maintainable, scalable routing system that integrates seamlessly with your existing architecture while adhering to modern development best practices.

### User:

# 🎮 Gamification & Rewards Framework for **Tidaro**
---
## 1. **Core Mechanics** (MVP-ready)
* **Points System:**
  * Earn “✨Spark Points” for bookings, reviews, referrals.
  * Example: `+100 points` per completed cleaning, `+50` for feedback.
* **Badges & Milestones:**
  * *Loyal Client* (10 bookings), *Eco-Pro* (5 eco-friendly cleanings), *Super Reviewer* (5 detailed reviews).
* **Progress Visuals:**
  * A simple progress bar on dashboard → “250/500 points to next reward.”
---
## 2. **Engagement Loops** (Habit-building)
* **Streaks:** Weekly/monthly booking streak bonuses.
* **Challenges:** Personalized quests (e.g., “Book a deep clean within 30 days → 500 points”).
* **Surprise Rewards:** Random discounts or hidden badges.
---
## 3. **Community & Competition**
* **Leaderboards:**
  * Weekly *Top Clients* & *Top Housekeepers*.
  * Segmented so casual users aren’t discouraged.
* **Social Sharing:**
  * Share badges on WhatsApp, Insta, or LinkedIn.
  * Example: “🏆 Just unlocked Eco-Friendly Pro on Tidaro!”
---
## 4. **Reward Layers**
### Virtual (low cost, instant):
* Spark Points (redeemable in-app).
* Unlock cosmetic perks → profile themes, premium avatars.
### Real-world (high impact):
* **Discounts:** 5–10% off after 5 bookings.
* **Free Add-ons:** Window cleaning or laundry bonus.
* **Tiered Perks:**
  * *Gold* → priority booking.
  * *Platinum* → free cancellation + dedicated support.
* **Partner Rewards:**
  * Coffee vouchers ☕, meal delivery discounts 🍽️, home supplies 🧽.
---
## 5. **Best Practices**
* Keep it **lightweight at launch** → Points + Progress Bar + 1–2 Badges.
* Integrate **Supabase** for tracking points/badges linked to bookings.
* Use **feature flags/A-B testing** to test new rewards gradually.
* Blend **intrinsic motivation** (*my home is clean, I’m proud*) with **extrinsic perks** (*points, discounts*).
---
## 6. **Future Expansion**
* Housekeeper-side gamification → reward punctuality, high ratings, eco-service use.
* “Team goals” → clients & cleaners can hit shared milestones.
* Seasonal campaigns (Ramadan specials, Eid cleaning bonuses).
---
⚡ **Key Hook for Morocco**:
* Rewards linked with **local culture & lifestyle** (coffee, pastries, market deals).
* Gamification should feel **community-driven**, not just “points farming.”



### Assistant:
<details type="reasoning" done="false">
<summary>Thinking…</summary>
> We're going to design a gamification framework for Tidaro that fits into our existing architecture. Let's break down the requirements and implement them step by step.
> 
> First, let's understand what we need:
> 1. Points system tied to actions (bookings, reviews, referrals)
> 2. Badges and milestones
> 3. Progress visuals
> 4. Engagement loops (streaks, challenges)
> 5. Community elements (leaderboards, social sharing)
> 6. Reward tiers (virtual and real-world)
> 
> We'll integrate this with our existing tech stack:
> - Flutter for frontend
> - Supabase for backend
> - Riverpod/Bloc for state management
> - fppdart for functional programming
> 
> Let's start by defining the core components:
> 
> ### 1. Points System
> We'll create a `PointsManager` that tracks points earned from different activities.
> 
> ### 2. Badge System
> We'll have a `BadgeSystem` that checks for badge unlocks based on user activity.
> 
> ### 3. Progress Tracking
> We'll track user progress toward milestones and display it visually.
> 
> ### 4. Leaderboard System
> We'll create a leaderboard that shows top users and housekeepers.
> 
> ### 5. Reward Redemption
> We'll allow users to redeem points for various rewards.
> 
> Now, let's implement these components:
> 
> ```dart
> // lib/features/gamification/data/models/points_transaction.dart
> import 'package:equatable/equatable.dart';
> 
> class PointsTransaction extends Equatable {
>   final String id;
>   final int points;
>   final String type; // booking, review, referral, streak_bonus
>   final DateTime timestamp;
>   final String description;
> 
>   const PointsTransaction({
>     required this.id,
>     required this.points,
>     required this.type,
>     required this.timestamp,
>     required this.description,
>   });
> 
>   @override
>   List<Object> get props => [id, points, type, timestamp, description];
> }
> 
> // lib/features/gamification/data/models/badge.dart
> import 'package:equatable/equatable.dart';
> 
> class Badge extends Equatable {
>   final String id;
>   final String name;
>   final String icon;
>   final String description;
>   final bool isUnlocked;
> 
>   const Badge({
>     required this.id,
>     required this.name,
>     required this.icon,
>     required this.description,
>     required this.isUnlocked,
>   });
> 
>   @override
>   List<Object> get props => [id, name, icon, description, isUnlocked];
> }
> 
> // lib/features/gamification/data/models/progress.dart
> import 'package:equatable/equatable.dart';
> 
> class Progress extends Equatable {
>   final int currentPoints;
>   final int pointsToNextLevel;
>   final double percentageComplete;
> 
>   const Progress({
>     required this.currentPoints,
>     required this.pointsToNextLevel,
>     required this.percentageComplete,
>   });
> 
>   @override
>   List<Object> get props => [currentPoints, pointsToNextLevel, percentageComplete];
> }
> 
> // lib/features/gamification/data/models/leaderboard_entry.dart
> import 'package:equatable/equatable.dart';
> 
> class LeaderboardEntry extends Equatable {
>   final String userId;
>   final String userName;
>   final String avatarUrl;
>   final int totalPoints;
>   final int rank;
> 
>   const LeaderboardEntry({
>     required this.userId,
>     required this.userName,
>     required this.avatarUrl,
>     required this.totalPoints,
>     required this.rank,
>   });
> 
>   @override
>   List<Object> get props => [userId, userName, avatarUrl, totalPoints, rank];
> }
> ```
> 
> Now, let's create the repository interface:
> 
> ```dart
> // lib/features/gamification/domain/repositories/gamification_repository.dart
> import 'package:fpdart/fpdart.dart';
> import 'package:my_app/features/gamification/data/models/badge.dart';
> import 'package:my_app/features/gamification/data/models/leaderboard_entry.dart';
> import 'package:my_app/features/gamification/data/models/points_transaction.dart';
> import 'package:my_app/features/gamification/data/models/progress.dart';
> 
> abstract class IGamificationRepository {
>   Future<Either<Exception, PointsTransaction>> addPoints({
>     required String userId,
>     required int points,
>     required String type,
>     required String description,
>   });
> 
>   Future<Either<Exception, List<PointsTransaction>>> getUserTransactions({
>     required String userId,
>   });
> 
>   Future<Either<Exception, List<Badge>>> getUserBadges({
>     required String userId,
>   });
> 
>   Future<Either<Exception, Progress>> getUserProgress({
>     required String userId,
>   });
> 
>   Future<Either<Exception, List<LeaderboardEntry>>> getLeaderboard({
>     required String category, // 'clients' or 'cleaners'
>   });
> 
>   Future<Either<Exception, bool>> unlockBadge({
>     required String userId,
>     required String badgeId,
>   });
> }
> ```
> 
> Now, let's implement the repository using Supabase:
> 
> ```dart
> // lib/features/gamification/data/repositories/gamification_repository_impl.dart
> import 'package:fpdart/fpdart.dart';
> import 'package:supabase_flutter/supabase_flutter.dart';
> import 'package:my_app/features/gamification/data/models/badge.dart';
> import 'package:my_app/features/gamification/data/models/leaderboard_entry.dart';
> import 'package:my_app/features/gamification/data/models/points_transaction.dart';
> import 'package:my_app/features/gamification/data/models/progress.dart';
> import 'package:my_app/features/gamification/domain/repositories/gamification_repository.dart';
> 
> class GamificationRepositoryImpl implements IGamificationRepository {
>   final SupabaseClient _supabase;
> 
>   GamificationRepositoryImpl(this._supabase);
> 
>   @override
>   Future<Either<Exception, PointsTransaction>> addPoints({
>     required String userId,
>     required int points,
>     required String type,
>     required String description,
>   }) async {
>     try {
>       final response = await _supabase
>           .from('points_transactions')
>           .insert({
>             'user_id': userId,
>             'points': points,
>             'type': type,
>             'description': description,
>           })
>           .select()
>           .single();
> 
>       return right(PointsTransaction.fromJson(response));
>     } catch (e) {
>       return left(Exception('Failed to add points: $e'));
>     }
>   }
> 
>   @override
>   Future<Either<Exception, List<PointsTransaction>>> getUserTransactions({
>     required String userId,
>   }) async {
>     try {
>       final response = await _supabase
>           .from('points_transactions')
>           .select()
>           .eq('user_id', userId)
>           .order('timestamp', ascending: false);
> 
>       return right(
>         response.map((json) => PointsTransaction.fromJson(json)).toList(),
>       );
>     } catch (e) {
>       return left(Exception('Failed to load transactions: $e'));
>     }
>   }
> 
>   @override
>   Future<Either<Exception, List<Badge>>> getUserBadges({
>     required String userId,
>   }) async {
>     try {
>       final response = await _supabase
>           .from('badges')
>           .select()
>           .eq('user_id', userId);
> 
>       return right(
>         response.map((json) => Badge.fromJson(json)).toList(),
>       );
>     } catch (e) {
>       return left(Exception('Failed to load badges: $e'));
>     }
>   }
> 
>   @override
>   Future<Either<Exception, Progress>> getUserProgress({
>     required String userId,
>   }) async {
>     try {
>       // Get current points
>       final pointsResponse = await _supabase
>           .from('points_transactions')
>           .select('SUM(points)')
>           .eq('user_id', userId)
>           .single();
> 
>       final currentPoints = pointsResponse['sum'] ?? 0;
> 
>       // Calculate points needed for next level (example: 500 points per level)
>       final pointsToNextLevel = 500 - (currentPoints % 500);
>       final percentageComplete = (currentPoints % 500) / 500 * 100;
> 
>       return right(
>         Progress(
>           currentPoints: currentPoints,
>           pointsToNextLevel: pointsToNextLevel,
>           percentageComplete: percentageComplete,
>         ),
>       );
>     } catch (e) {
>       return left(Exception('Failed to calculate progress: $e'));
>     }
>   }
> 
>   @override
>   Future<Either<Exception, List<LeaderboardEntry>>> getLeaderboard({
>     required String category,
>   }) async {
>     try {
>       final response = await _supabase
>           .from('users')
>           .select('id, name, avatar_url, SUM(points_transactions.points) as total_points')
>           .eq('role', category)
>           .groupBy('id')
>           .order('total_points', ascending: false)
>           .limit(10);
> 
>       return right(
>         response.map((json) => LeaderboardEntry.fromJson(json)).toList(),
>       );
>     } catch (e) {
>       return left(Exception('Failed to load leaderboard: $e'));
>     }
>   }
> 
>   @override
>   Future<Either<Exception, bool>> unlockBadge({
>     required String userId,
>     required String badgeId,
>   }) async {
>     try {
>       await _supabase
>           .from('badges')
>           .update({'unlocked_at': DateTime.now()})
>           .eq('user_id', userId)
>           .eq('badge_id', badgeId);
> 
>       return right(true);
>     } catch (e) {
>       return left(Exception('Failed to unlock badge: $e'));
>     }
>   }
> }
> ```
> 
> Now, let's create the use cases:
> 
> ```dart
> // lib/features/gamification/domain/usecases/add_points_usecase.dart
> import 'package:fpdart/fpdart.dart';
> import 'package:my_app/features/gamification/domain/repositories/gamification_repository.dart';
> 
> class AddPointsUseCase {
>   final IGamificationRepository _repository;
> 
>   AddPointsUseCase(this._repository);
> 
>   Future<Either<Exception, PointsTransaction>> call({
>     required String userId,
>     required int points,
>     required String type,
>     required String description,
>   }) async {
>     return await _repository.addPoints(
>       userId: userId,
>       points: points,
>       type: type,
>       description: description,
>     );
>   }
> }
> ```
> 
> For the badge system, we can create a use case to check for badge unlocks:
> 
> ```dart
> // lib/features/gamification/domain/usecases/check_badge_unlocks_usecase.dart
> import 'package:fpdart/fpdart.dart';
> import 'package:my_app/features/gamification/domain/repositories/gamification_repository.dart';
> 
> class CheckBadgeUnlocksUseCase {
>   final IGamificationRepository _repository;
> 
>   CheckBadgeUnlocksUseCase(this._repository);
> 
>   Future<Either<Exception, List<Badge>>> call({
>     required String userId,
>   }) async {
>     // Get current badges
>     final badgesResult = await _repository.getUserBadges(userId: userId);
>     
>     return badgesResult.fold(
>       (exception) => left(exception),
>       (badges) async {
>         // Check which badges can be unlocked
>         final unlockedBadges = <Badge>[];
>         
>         // Example: Loyal Client badge (10 bookings)
>         final bookingCount = await _repository.getBookingCount(userId);
>         if (bookingCount >= 10 && !badges.any((b) => b.id == 'loyal_client')) {
>           unlockedBadges.add(Badge(
>             id: 'loyal_client',
>             name: 'Loyal Client',
>             icon: '👑',
>             description: 'Completed 10 bookings',
>             isUnlocked: false,
>           ));
>         }
>         
>         // Add more badge checks here
>         
>         return right(unlockedBadges);
>       },
>     );
>   }
> }
> ```
> 
> Now, let's create the BLoC for the gamification screen:
> 
> ```dart
> // lib/features/gamification/presentation/blocs/gamification_bloc.dart
> import 'package:flutter_bloc/flutter_bloc.dart';
> import 'package:fpdart/fpdart.dart';
> import 'package:my_app/features/gamification/domain/usecases/add_points_usecase.dart';
> import 'package:my_app/features/gamification/domain/usecases/get_user_progress_usecase.dart';
> import 'package:my_app/features/gamification/domain/usecases/get_user_badges_usecase.dart';
> import 'package:my_app/features/gamification/domain/usecases/get_leaderboard_usecase.dart';
> import 'package:my_app/features/gamification/data/models/badge.dart';
> import 'package:my_app/features/gamification/data/models/progress.dart';
> import 'package:my_app/features/gamification/data/models/leaderboard_entry.dart';
> 
> part 'gamification_event.dart';
> part 'gamification_state.dart';
> 
> class GamificationBloc extends Bloc<GamificationEvent, GamificationState> {
>   final AddPointsUseCase _addPointsUseCase;
>   final GetUserProgressUseCase _getUserProgressUseCase;
>   final GetUserBadgesUseCase _getUserBadgesUseCase;
>   final GetLeaderboardUseCase _getLeaderboardUseCase;
> 
>   GamificationBloc({
>     required AddPointsUseCase addPointsUseCase,
>     required GetUserProgressUseCase getUserProgressUseCase,
>     required GetUserBadgesUseCase getUserBadgesUseCase,
>     required GetLeaderboardUseCase getLeaderboardUseCase,
>   })  : _addPointsUseCase = addPointsUseCase,
>         _getUserProgressUseCase = getUserProgressUseCase,
>         _getUserBadgesUseCase = getUserBadgesUseCase,
>         _getLeaderboardUseCase = getLeaderboardUseCase,
>         super(GamificationInitial()) {
>     on<LoadGamificationData>(_loadData);
>     on<AddPoints>(_addPoints);
>   }
> 
>   Future<void> _loadData(
>     LoadGamificationData event,
>     Emitter<GamificationState> emit,
>   ) async {
>     emit(GamificationLoading());
> 
>     // Load progress
>     final progressResult = await _getUserProgressUseCase(event.userId);
>     final badgesResult = await _getUserBadgesUseCase(event.userId);
>     final leaderboardResult = await _getLeaderboardUseCase('clients');
> 
>     progressResult.fold(
>       (exception) => emit(GamificationError(message: exception.toString())),
>       (progress) => badgesResult.fold(
>         (exception) => emit(GamificationError(message: exception.toString())),
>         (badges) => leaderboardResult.fold(
>           (exception) => emit(GamificationError(message: exception.toString())),
>           (leaderboard) => emit(
>             GamificationLoaded(
>               progress: progress,
>               badges: badges,
>               leaderboard: leaderboard,
>             ),
>           ),
>         ),
>       ),
>     );
>   }
> 
>   Future<void> _addPoints(
>     AddPoints event,
>     Emitter<GamificationState> emit,
>   ) async {
>     final result = await _addPointsUseCase(
>       userId: event.userId,
>       points: event.points,
>       type: event.type,
>       description: event.description,
>     );
> 
>     result.fold(
>       (exception) => emit(GamificationError(message: exception.toString())),
>       (_) => add(LoadGamificationData(userId: event.userId)),
>     );
>   }
> }
> ```
> 
> Finally, let's create the UI components:
> 
> ```dart
> // lib/features/gamification/presentation/screens/gamification_screen.dart
> import 'package:flutter/material.dart';
> import 'package:flutter_bloc/flutter_bloc.dart';
> import 'package:my_app/features/gamification/presentation/blocs/gamification_bloc.dart';
> import 'package:my_app/features/gamification/presentation/widgets/progress_bar_widget.dart';
> import 'package:my_app/features/gamification/presentation/widgets/badge_grid_widget.dart';
> import 'package:my_app/features/gamification/presentation/widgets/leaderboard_widget.dart';
> 
> class GamificationScreen extends StatelessWidget {
>   final String userId;
> 
>   const GamificationScreen({required this.userId, Key? key}) : super(key: key);
> 
>   @override
>   Widget build(BuildContext context) {
>     return BlocProvider(
>       create: (context) => GamificationBloc(
>         addPointsUseCase: context.read<AddPointsUseCase>(),
>         getUserProgressUseCase: context.read<GetUserProgressUseCase>(),
>         getUserBadgesUseCase: context.read<GetUserBadgesUseCase>(),
>         getLeaderboardUseCase: context.read<GetLeaderboardUseCase>(),
>       )..add(LoadGamificationData(userId: userId)),
>       child: Scaffold(
>         appBar: AppBar(title: const Text('Gamification')),
>         body: Padding(
>           padding: const EdgeInsets.all(16.0),
>           child: Column(
>             crossAxisAlignment: CrossAxisAlignment.start,
>             children: [
>               // Progress section
>               BlocBuilder<GamificationBloc, GamificationState>(
>                 builder: (context, state) {
>                   if (state is GamificationLoaded) {
>                     return ProgressBarWidget(progress: state.progress);
>                   }
>                   return const CircularProgressIndicator();
>                 },
>               ),
> 
>               const SizedBox(height: 20),
> 
>               // Badges section
>               BlocBuilder<GamificationBloc, GamificationState>(
>                 builder: (context, state) {
>                   if (state is GamificationLoaded) {
>                     return BadgeGridWidget(badges: state.badges);
>                   }
>                   return const CircularProgressIndicator();
>                 },
>               ),
> 
>               const Spacer(),
> 
>               // Leaderboard section
>               BlocBuilder<GamificationBloc, GamificationState>(
>                 builder: (context, state) {
>                   if (state is GamificationLoaded) {
>                     return LeaderboardWidget(leaderboard: state.leaderboard);
>                   }
>                   return const CircularProgressIndicator();
>                 },
>               ),
>             ],
>           ),
>         ),
>       ),
>     );
>   }
> }
> ```
> 
> And the widgets:
> 
> ```dart
> // lib/features/gamification/presentation/widgets/progress_bar_widget.dart
> import 'package:flutter/material.dart';
> import 'package:my_app/features/gamification/data/models/progress.dart';
> 
> class ProgressBarWidget extends StatelessWidget {
>   final Progress progress;
> 
>   const ProgressBarWidget({required this.progress, Key? key}) : super(key: key);
> 
>   @override
>   Widget build(BuildContext context) {
>     return Card(
>       elevation: 4,
>       shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
>       child: Padding(
>         padding: const EdgeInsets.all(16.0),
>         child: Column(
>           crossAxisAlignment: CrossAxisAlignment.start,
>           children: [
>             Row(
>               mainAxisAlignment: MainAxisAlignment.spaceBetween,
>               children: [
>                 Text('${progress.currentPoints} Spark Points'),
>                 Text('${progress.pointsToNextLevel} to Next Level'),
>               ],
>             ),
>             const SizedBox(height: 8),
>             LinearProgressIndicator(
>               value: progress.percentageComplete / 100,
>               minHeight: 12,
>               borderRadius: BorderRadius.circular(6),
>             ),
>           ],
>         ),
>       ),
>     );
>   }
> }
> ```
> 
> ```dart
> // lib/features/gamification/presentation/widgets/badge_grid_widget.dart
> import 'package:flutter/material.dart';
> import 'package:my_app/features/gamification/data/models/badge.dart';
> 
> class BadgeGridWidget extends StatelessWidget {
>   final List<Badge> badges;
> 
>   const BadgeGridWidget({required this.badges, Key? key}) : super(key: key);
> 
>   @override
>   Widget build(BuildContext context) {
>     return GridView.builder(
>       shrinkWrap: true,
>       physics: const NeverScrollableScrollPhysics(),
>       gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
>         crossAxisCount: 3,
>         crossAxisSpacing: 16,
>         mainAxisSpacing: 16,
>       ),
>       itemCount: badges.length,
>       itemBuilder: (context, index) {
>         final badge = badges[index];
>         return Card(
>           elevation: 4,
>           shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
>           child: Column(
>             mainAxisAlignment: MainAxisAlignment.center,
>             children: [
>               Icon(
>                 Icons.star,
>                 size: 40,
>                 color: badge.isUnlocked ? Colors.yellow : Colors.grey,
>               ),
>               const SizedBox(height: 8),
>               Text(
>                 badge.name,
>                 style: TextStyle(fontWeight: FontWeight.bold),
>                 textAlign: TextAlign.center,
>               ),
>               const SizedBox(height: 4),
>               Text(
>                 badge.description,
>                 style: TextStyle(fontSize: 12),
>                 textAlign: TextAlign.center,
>               ),
>             ],
>           ),
>         );
>       },
>     );
>   }
> }
> ```
> 
> ```dart
> // lib/features/gamification/presentation/widgets/leaderboard_widget.dart
> import 'package:flutter/material.dart';
> import 'package:my_app/features/gamification/data/models/leaderboard_entry.dart';
> 
> class LeaderboardWidget extends StatelessWidget {
>   final List<LeaderboardEntry> leaderboard;
> 
>   const LeaderboardWidget({required this.leaderboard, Key? key}) : super(key: key);
> 
>   @override
>   Widget build(BuildContext context) {
>     return Card(
>       elevation: 4,
>       shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
>       child: ListView.builder(
>         shrinkWrap: true,
>         physics: const NeverScrollableScrollPhysics(),
>         itemCount: leaderboard.length,
>         itemBuilder: (context, index) {
>           final entry = leaderboard[index];
>           return ListTile(
>             leading: Text('#${entry.rank}'),
>             title: Text(entry.userName),
>             subtitle: Text('${entry.totalPoints} points'),
>             trailing: CircleAvatar(
>               backgroundImage: NetworkImage(entry.avatarUrl),
>             ),
>           );
>         },
>       ),
>     );
>   }
> }
> ```
> 
> This implementation provides a complete gamification framework that:
> 1. Tracks points for various activities
> 2. Unlocks badges based on user achievements
> 3. Shows progress toward next rewards
> 4. Displays leaderboards for competition
> 5. Integrates with Supabase for persistent storage
> 6. Follows Clean Architecture principles
> 7. Uses fpdart for safe error handling
> 8. Uses BLoC for state management
> 
> You can extend this further by adding:
> - Streak bonuses for consecutive bookings
> - Challenges for specific tasks
> - Social sharing functionality
> - Localized rewards for Moroccan users
> 
> Remember to test each component thoroughly and use feature flags to roll out new gamification features incrementally..

### Assistant:
<details type="reasoning" done="true" duration="4">
<summary>Thought for 4 seconds</summary>
> We're going to design a gamification framework for Tidaro that integrates with our existing tech stack (Flutter, Supabase, Bloc, fppdart). Let's break down the key components and provide code examples.
> 
> First, let's understand the requirements:
> 1. Points system tied to actions (bookings, reviews, referrals)
> 2. Badges and milestones
> 3. Progress visuals
> 4. Engagement loops (streaks, challenges)
> 5. Community features (leaderboards, social sharing)
> 6. Reward tiers (virtual and real-world)
> 
> Let's start by defining the core entities and then implement them in our architecture.
> 
> ### Step 1: Define Core Entities
> 
> We'll create these domain entities:
> - `PointTransaction`: Records point changes
> - `Badge`: Represents achievements
> - `UserProgress`: Tracks user's current progress
> - `Challenge`: Time-limited tasks for extra rewards
> 
> ### Step 2: Implement Data Layer
> 
> We'll need to store:
> - User points balance
> - Unlocked badges
> - Active challenges
> - Leaderboard positions
> 
> ### Step 3: Implement Presentation Layer
> 
> We'll create:
> - Points counter widget
> - Badge display section
> - Progress bar
> - Challenges list
> - Leaderboard view
> 
> Let's start coding:
> 
> ### Core Entities (Domain Layer)
</details>
# 🎮 Gamification Framework Implementation for Tidaro

Here's a complete implementation plan with code examples for integrating gamification into your Tidaro app:

## 1. Core Entities (Domain Layer)
```dart
// domain/entities/gamification_entities.dart
import 'package:fpdart/fpdart.dart';

sealed class PointTransaction {
  final int points;
  final DateTime timestamp;
  final String reason;

  PointTransaction({
    required this.points,
    required this.timestamp,
    required this.reason,
  });
}

class BookingPoints extends PointTransaction {
  BookingPoints(int points, DateTime timestamp)
      : super(points: points, timestamp: timestamp, reason: 'Booking completed');
}

class ReviewPoints extends PointTransaction {
  ReviewPoints(int points, DateTime timestamp)
      : super(points: points, timestamp: timestamp, reason: 'Review submitted');
}

class ReferralPoints extends PointTransaction {
  ReferralPoints(int points, DateTime timestamp)
      : super(points: points, timestamp: timestamp, reason: 'Referral successful');
}

class Badge {
  final String id;
  final String title;
  final String description;
  final IconData icon;
  final int requiredPoints;

  Badge({
    required this.id,
    required this.title,
    required this.description,
    required this.icon,
    required this.requiredPoints,
  });
}

class UserProgress {
  final int totalPoints;
  final List<PointTransaction> transactions;
  final List<String> unlockedBadges;
  final Map<String, int> streaks; // e.g., {'weekly_booking_streak': 3}

  UserProgress({
    required this.totalPoints,
    required this.transactions,
    required this.unlockedBadges,
    required this.streaks,
  });
}
```

## 2. Data Layer (Supabase Integration)
```dart
// data/datasources/gamification_datasource.dart
import 'package:supabase_flutter/supabase_flutter.dart';
import '../../domain/entities/gamification_entities.dart';

class GamificationDataSource {
  final SupabaseClient _client;

  GamificationDataSource(this._client);

  Future<Either<Exception, UserProgress>> getUserProgress(String userId) async {
    try {
      final response = await _client
          .from('user_progress')
          .select()
          .eq('user_id', userId)
          .maybeSingle();

      if (response == null) {
        return right(UserProgress(
          totalPoints: 0,
          transactions: [],
          unlockedBadges: [],
          streaks: {},
        ));
      }

      final transactionsResponse = await _client
          .from('point_transactions')
          .select()
          .eq('user_id', userId)
          .order('timestamp', ascending: false);

      final badgeIds = (response['unlocked_badges'] as List<dynamic>)
          .map((id) => id as String)
          .toList();

      return right(UserProgress(
        totalPoints: response['total_points'],
        transactions: transactionsResponse.map((t) => _parseTransaction(t)).toList(),
        unlockedBadges: badgeIds,
        streaks: Map<String, int>.from(response['streaks']),
      ));
    } catch (e) {
      return left(Exception('Failed to load user progress'));
    }
  }

  PointTransaction _parseTransaction(Map<String, dynamic> data) {
    final type = data['type'];
    switch (type) {
      case 'booking':
        return BookingPoints(data['points'], DateTime.parse(data['timestamp']));
      case 'review':
        return ReviewPoints(data['points'], DateTime.parse(data['timestamp']));
      case 'referral':
        return ReferralPoints(data['points'], DateTime.parse(data['timestamp']));
      default:
        throw Exception('Unknown transaction type');
    }
  }

  Future<Either<Exception, void>> addPoints({
    required String userId,
    required int points,
    required String reason,
  }) async {
    try {
      final transaction = _createTransaction(points, reason);
      await _client.from('point_transactions').insert({
        'user_id': userId,
        'points': points,
        'reason': reason,
        'type': _getTransactionType(transaction),
        'timestamp': DateTime.now().toIso8601String(),
      });

      // Update user progress
      final currentProgress = await getUserProgress(userId);
      if (currentProgress.isRight()) {
        final updatedPoints = currentProgress.right.totalPoints + points;
        await _client
            .from('user_progress')
            .update({'total_points': updatedPoints})
            .eq('user_id', userId);
      }

      return right(null);
    } catch (e) {
      return left(Exception('Failed to add points'));
    }
  }

  PointTransaction _createTransaction(int points, String reason) {
    if (reason.contains('booking')) {
      return BookingPoints(points, DateTime.now());
    } else if (reason.contains('review')) {
      return ReviewPoints(points, DateTime.now());
    } else if (reason.contains('referral')) {
      return ReferralPoints(points, DateTime.now());
    }
    throw Exception('Unknown transaction reason');
  }

  String _getTransactionType(PointTransaction transaction) {
    if (transaction is BookingPoints) return 'booking';
    if (transaction is ReviewPoints) return 'review';
    if (transaction is ReferralPoints) return 'referral';
    throw Exception('Unknown transaction type');
  }
}
```

## 3. Business Logic (Domain Layer)
```dart
// domain/usecases/gamification_usecases.dart
import 'package:fpdart/fpdart.dart';
import '../../data/datasources/gamification_datasource.dart';
import '../../domain/entities/gamification_entities.dart';

class AddPointsUseCase {
  final GamificationDataSource _dataSource;

  AddPointsUseCase(this._dataSource);

  Future<Either<Exception, void>> execute({
    required String userId,
    required int points,
    required String reason,
  }) async {
    return _dataSource.addPoints(userId: userId, points: points, reason: reason);
  }
}

class GetBadgesUseCase {
  final GamificationDataSource _dataSource;

  GetBadgesUseCase(this._dataSource);

  Future<Either<Exception, List<Badge>>> execute(String userId) async {
    try {
      final progress = await _dataSource.getUserProgress(userId);
      if (progress.isLeft()) return left(progress.left);

      final badges = [
        Badge(
          id: 'loyal_client',
          title: 'Loyal Client',
          description: 'Complete 10 bookings',
          icon: Icons.star,
          requiredPoints: 1000,
        ),
        Badge(
          id: 'eco_pro',
          title: 'Eco-Pro',
          description: 'Complete 5 eco-friendly cleanings',
          icon: Icons.eco,
          requiredPoints: 750,
        ),
        Badge(
          id: 'super_reviewer',
          title: 'Super Reviewer',
          description: 'Submit 5 detailed reviews',
          icon: Icons.comment,
          requiredPoints: 500,
        ),
      ];

      return right(badges.where((badge) {
        final earned = progress.right.totalPoints >= badge.requiredPoints;
        return earned && !progress.right.unlockedBadges.contains(badge.id);
      }).toList());
    } catch (e) {
      return left(Exception('Failed to load badges'));
    }
  }
}
```

## 4. State Management (BLoC)
```dart
// presentation/blocs/gamification_bloc.dart
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:fpdart/fpdart.dart';
import '../../domain/usecases/gamification_usecases.dart';

enum GamificationStatus { initial, loading, loaded, error }

class GamificationState {
  final GamificationStatus status;
  final UserProgress? progress;
  final List<Badge>? availableBadges;
  final Either<Exception, void>? lastActionResult;

  GamificationState({
    required this.status,
    this.progress,
    this.availableBadges,
    this.lastActionResult,
  });
}

class GamificationCubit extends Cubit<GamificationState> {
  final GetBadgesUseCase _getBadgesUseCase;
  final AddPointsUseCase _addPointsUseCase;

  GamificationCubit(this._getBadgesUseCase, this._addPointsUseCase)
      : super(GamificationState(status: GamificationStatus.initial));

  Future<void> loadProgress(String userId) async {
    emit(state.copyWith(status: GamificationStatus.loading));
    final result = await _getBadgesUseCase.execute(userId);
    result.fold(
      (exception) => emit(state.copyWith(
        status: GamificationStatus.error,
        lastActionResult: Left(exception),
      )),
      (badges) => emit(state.copyWith(
        status: GamificationStatus.loaded,
        progress: state.progress,
        availableBadges: badges,
      )),
    );
  }

  Future<void> addPoints({
    required String userId,
    required int points,
    required String reason,
  }) async {
    emit(state.copyWith(status: GamificationStatus.loading));
    final result = await _addPointsUseCase.execute(userId, points, reason);
    result.fold(
      (exception) => emit(state.copyWith(
        status: GamificationStatus.error,
        lastActionResult: Left(exception),
      )),
      (_) => loadProgress(userId), // Refresh progress after adding points
    );
  }
}
```

## 5. UI Components
```dart
// presentation/widgets/spark_points_counter.dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

class SparkPointsCounter extends StatelessWidget {
  final String userId;

  const SparkPointsCounter({required this.userId, Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BlocConsumer<GamificationCubit, GamificationState>(
      listener: (context, state) {
        if (state.status == GamificationStatus.error) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error: ${state.lastActionResult?.left}')),
          );
        }
      },
      builder: (context, state) {
        if (state.status == GamificationStatus.loading) {
          return const CircularProgressIndicator();
        }

        return Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '${state.progress?.totalPoints ?? 0}',
                  style: Theme.of(context).textTheme.headlineMedium,
                ),
                const Icon(Icons.sparkles, color: Colors.amber),
              ],
            ),
            const SizedBox(height: 8),
            LinearProgressIndicator(
              value: state.progress != null
                  ? state.progress!.totalPoints / 1000 // Next milestone
                  : 0,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => context.read<GamificationCubit>().addPoints(
                    userId: userId,
                    points: 100,
                    reason: 'Booking completed',
                  ),
              child: const Text('Complete Booking (+100)'),
            ),
          ],
        );
      },
    );
  }
}
```

## 6. Challenge Component
```dart
// presentation/widgets/challenge_card.dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

class ChallengeCard extends StatelessWidget {
  final String title;
  final String description;
  final int reward;
  final VoidCallback onComplete;

  const ChallengeCard({
    required this.title,
    required this.description,
    required this.reward,
    required this.onComplete,
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment-between,
              children: [
                Text(title, style: Theme.of(context).textTheme.titleLarge),
                Row(
                  children: [
                    const Icon(Icons.star, color: Colors.amber),
                    Text('+ $reward', style: TextStyle(color: Colors.amber)),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(description),
            const Spacer(),
            Align(
              alignment: Alignment.bottomRight,
              child: ElevatedButton(
                onPressed: onComplete,
                child: const Text('Complete'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

## 7. Leaderboard Component
```dart
// presentation/screens/leaderboard_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

class LeaderboardScreen extends StatelessWidget {
  final String userId;

  const LeaderboardScreen({required this.userId, Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Leaderboard')),
      body: ListView(
        children: [
          ListTile(
            leading: const Icon(Icons.trophy, color: Colors.amber),
            title: const Text('Your Rank'),
            subtitle: const Text('#42'),
          ),
          const Divider(),
          for (int i = 1; i <= 10; i++)
            ListTile(
              leading: Text('$i', style: const TextStyle(fontWeight: FontWeight.bold)),
              title: Text('User #$i'),
              trailing: Text('${1000 + i * 50} points'),
            ),
        ],
      ),
    );
  }
}
```

## 8. Social Sharing Integration
```dart
// presentation/utils/social_sharing.dart
import 'package:share_plus/share_plus.dart';

Future<void> shareAchievement(Badge badge) async {
  await Share.share(
    '🏆 Just unlocked "${badge.title}" on Tidaro!\n${badge.description}',
    subject: 'New Achievement Unlocked!',
  );
}
```

## Implementation Roadmap
1. **Phase 1 (MVP)**:
   - Points system for bookings/reviews
   - Basic progress bar
   - 2-3 badge types
   - Simple leaderboard

2. **Phase 2**:
   - Streaks and challenges
   - Partner rewards integration
   - Social sharing

3. **Phase 3**:
   - Housekeeper gamification
   - Team goals
   - Seasonal campaigns

This framework maintains separation of concerns, uses functional patterns with fpdart, and leverages your existing tech stack while providing engaging gamification experiences tailored to Moroccan users.

