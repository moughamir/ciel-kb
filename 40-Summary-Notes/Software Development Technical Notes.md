# Software Development Technical Notes

This note summarizes various technical discussions related to software development, including refactoring, project setup, and testing.

## PHP to TypeScript Refactoring

-   **Process:** More than just syntax change; requires understanding TypeScript concepts and differences from PHP.
-   **Steps:**
    1.  Understand TypeScript concepts (interfaces, classes, enums, modules, generics).
    2.  Familiarize with TypeScript syntax.
    3.  Port PHP code to TypeScript line by line, replacing PHP-specific syntax.
    4.  Utilize TypeScript's type system for early error detection.
    5.  Test code thoroughly (Jest or Mocha).
    6.  Refactor to leverage TypeScript features (interfaces for types, classes for encapsulation).
-   **Architecture:** Microservices monorepo.
-   **Frontend:** React.
-   **Backend:** Express.js.
-   **Database:** PostgreSQL.
-   **Cache:** Redis.
-   **Real-time:** Socket.IO.
-   **Version Control:** Git.

## TypeScript Backend Project Setup (with PNPM and Express.js)

1.  **Install PNPM:** `npm install -g pnpm`
2.  **Create Project Directory:** `mkdir my-project && cd my-project`
3.  **Initialize PNPM Project:** `pnpm init -y`
4.  **Install Dependencies:** `pnpm install express @types/express typescript ts-node-dev --save-dev`
    -   `express`: Web framework.
    -   `@types/express`: TypeScript definitions for Express.
    -   `typescript`: TypeScript compiler.
    -   `ts-node-dev`: Hot-reloading for development.
5.  **Create `src` Directory:** `mkdir src`
6.  **Configure `tsconfig.json`:**
    ```json
    {
      "compilerOptions": {
        "lib": ["es6"],
        "module": "commonjs",
        "moduleResolution": "node",
        "target": "es6",
        "sourceMap": true,
        "outDir": "dist"
      },
      "include": ["src/**/*"]
    }
    ```
7.  **Create `src/index.ts`:**
    ```typescript
    import express from 'express';
    const app = express();
    app.get('/', (req, res) => { res.send('Hello World!'); });
    app.listen(3000, () => { console.log('Server is listening on port 3000!'); });
    ```
8.  **Add Scripts to `package.json`:**
    ```json
    "scripts": {
      "build": "tsc",
      "start": "ts-node-dev --respawn --transpileOnly src/index.ts"
    }
    ```
9.  **Start Server:** `pnpm start`

## Unit Testing Frameworks (Jest vs. Mocha)

-   **Jest:**
    -   **Pros:** Easy setup, built-in snapshot testing, mocking, code coverage, test runner. Popular for React.
    -   **Cons:** Can be slow for large codebases, difficult to configure for non-React projects.
-   **Mocha:**
    -   **Pros:** Flexible, supports asynchronous testing, multiple test styles, custom reporters, highly configurable.
    -   **Cons:** Requires additional libraries for mocking and code coverage.
-   **Choice:** Jest for React projects; Mocha for other JavaScript/TypeScript projects requiring more flexibility.

## JavaScript: Shallow vs. Deep Copy

-   **Shallow Copy:** Creates a new object/array but copies only references to nested data.
    -   **Primitives:** Creates independent copy.
    -   **Non-Primitives:** Shares nested objects/arrays; modifying copy affects original.
    -   **Methods:** `Array.prototype.slice()`, `Object.assign({}, obj)`.
-   **Deep Copy:** Creates a completely independent copy, including all nested objects/arrays.
    -   Recursively traverses and copies all nested structures.
    -   **Methods:** `JSON.parse(JSON.stringify())`, Lodash `cloneDeep`.
    -   **Limitations:** Resource-intensive, issues with functions/symbols, circular references.

## Related Documents

- [[30-All-Notes/PHP_UML_Design..md]]
- [[30-All-Notes/Entertainment_Recommendations..md]]
