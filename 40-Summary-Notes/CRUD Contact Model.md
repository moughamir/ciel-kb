# CRUD Contact Model

This note summarizes the design and implementation of a CRM system for managing contacts, utilizing FastAPI and PostgreSQL, with a focus on data modeling and API development.

## Technology Stack

-   **Backend Framework:** FastAPI (Python) - modern, efficient, high-performance, type hints, async support.
-   **Database:** PostgreSQL - robust, feature-rich, scalable, strong data integrity.

## Design Pattern & Architecture

-   **MVC (Model-View-Controller) Design Pattern:**
    -   **Model:** Data and business logic (contact models, DB interactions, validation).
    -   **View:** Presentation and UI (displaying info, forms, user interactions).
    -   **Controller:** Intermediary (handles requests, operations on model, updates view).
-   **Layered Architecture:**
    -   **Presentation Layer:** UI and user interactions (View, Controller).
    -   **Business Logic Layer:** Application logic and rules (Model, validation, data processing).
    -   **Data Access Layer:** Data storage and retrieval (CRUD with PostgreSQL).
-   **Additional Considerations:** Authentication/Authorization, RESTful API design, Error Handling, Scalability/Performance (caching, load balancing, DB optimization).

## Contact Data Model (Pydantic)

The `Contact` model evolves to support rich contact information:

-   **`PhoneNumber` Model:** `number: str`, `label: str` (e.g., "Home", "Work", "Mobile").
-   **`Email` Model:** `address: str`, `label: str` (e.g., "Personal", "Work").
-   **`Country` Model:** `name: str`, `code: str`, `phone_extension: str`.
-   **`Address` Model:** `street: str`, `city: str`, `state: str`, `postal_code: str`, `label: str`, `country: Country`.
-   **`URLType` Enum:** `website`, `linkedin`, `twitter`, etc.
-   **`URL` Model:** `type: URLType`, with a dynamic `link` property generated based on `URLType` using a dictionary and lambda functions for efficiency.
-   **`Contact` Model:**
    -   `id: int`
    -   `first_name: str`, `last_name: str`
    -   `phone_numbers: List[PhoneNumber]`
    -   `emails: List[Email]`
    -   `addresses: List[Address]`
    -   `urls: List[URL]`
    -   `company: str`
    -   `notes: str`
    -   `is_professional: bool`

## FastAPI Integration (CRUD Operations)

-   **Initialization:** `app = FastAPI()`.
-   **In-memory Storage:** (for example) `contacts = []`.
-   **Routes:**
    -   `GET /contacts`: Get all contacts.
    -   `GET /contacts/{contact_id}`: Get contact by ID.
    -   `POST /contacts`: Create new contact.
    -   `PUT /contacts/{contact_id}`: Update existing contact.
    -   `DELETE /contacts/{contact_id}`: Delete contact.
-   **Running the App:** `uvicorn main:app --reload`.

## VCards (Virtual Contact Files)

-   **Purpose:** Standardized file format (`.vcf`) to store and exchange contact information.
-   **Helper Function (`generate_vcard`):** Takes a `Contact` object and generates a vCard string.
    -   Example route: `GET /vcards` to generate and download `contacts.vcf`.
-   **Specifications:** Defined by IETF (vCard 3.0 and 4.0).
-   **Key Aspects:** Version, Structure, Properties (name, address, phone, email, etc.), Parameters (TYPE, VALUE, PREF), Encoding (UTF-8), Extensibility.
-   **Differences (vCard 3.0 vs. 4.0):**
    -   **Syntax:** 3.0 line-based; 4.0 JSON-based, hierarchical.
    -   **Properties:** 4.0 has new/modified properties, more comprehensive.
    -   **Parameters:** 4.0 standardized handling, new syntax.
    -   **Data Types:** 4.0 richer (dates, durations, binary).
    -   **Multilingual Support:** 4.0 enhanced with `LANGUAGE` parameter.
    -   **Extensibility:** 4.0 improved mechanisms.
    -   **Versioning:** 4.0 clearer version indicators.
-   **Example vCard 4.0:** Structured format including `N`, `FN`, `ORG`, `TITLE`, `TEL`, `EMAIL`, `ADR`, `URL`, `NOTE` properties.

## Related Documents

- [[30-All-Notes/CRUD_Contact_Model.md]]
