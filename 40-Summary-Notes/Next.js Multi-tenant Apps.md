# Next.js Multi-tenant Apps

This note summarizes the discussion on using Next.js for building multi-tenant applications, including its suitability and examples.

## Suitability of Next.js for Multi-tenancy

-   Next.js is a good choice for creating multi-tenant applications due to its features for building scalable applications.
-   **Key Features:**
    -   Server-Side Rendering (SSR) for fast page loads.
    -   Automatic code splitting.
    -   Easy deployment.
    -   Built-in support for dynamic routing.
-   **Implementation:**
    -   Combine dynamic routing and environment variables to create unique pages/content for each tenant.
    -   Use a database to store tenant-specific data.
    -   Server-side rendering to dynamically generate pages based on tenant data.

## Examples of Multi-tenant Apps with Next.js

-   **Saaskit:** An open-source project providing a multi-tenant app boilerplate with Next.js, Prisma, and Auth0. Includes user authentication, subscription management, and billing integration.
    -   [https://github.com/saaskit/saaskit](https://github.com/saaskit/saaskit)
-   **Raiondesu/multi-tenant-nextjs:** Demonstrates using Next.js with server-side rendering for separate subdomains and databases for each tenant. Uses `nextjs-middleware-tenant` package.
    -   [https://github.com/Raiondesu/multi-tenant-nextjs](https://github.com/Raiondesu/multi-tenant-nextjs)
-   **Vercel/next.js/examples/multi-tenant:** Shows how to create a multi-tenant app serving multiple websites from a single codebase using a custom server to determine the tenant based on the URL.
    -   [https://github.com/vercel/next.js/tree/canary/examples/multi-tenant](https://github.com/vercel/next.js/tree/canary/examples/multi-tenant)

## Related Documents

- [[30-All-Notes/Omnizya_Startup_Launch..md]]
