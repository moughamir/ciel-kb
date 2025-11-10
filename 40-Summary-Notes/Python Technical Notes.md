# Python Technical Notes

This note summarizes various technical discussions and code examples in Python.

## Organizing Markdown Files

-   A Python function to iterate through markdown files in a folder and organize them into date-based subfolders (e.g., `YYYY_MM_DD_timestamp_filename.md` into `YYYY_MM_DD/filename.md`).
-   Uses `os.listdir`, `os.path.join`, `datetime.strptime`, `os.makedirs`, and `shutil.move`.

## Salted Hasher and Decoder

-   **SaltedHasher Class:** Uses `hashlib` (SHA-256) and `os.urandom` for salting to hash strings.
    -   `generate_salt()`: Generates a random salt.
    -   `hash_string(raw_string, salt=None)`: Hashes the string with a generated or provided salt.
-   **SaltedHashDecoder Class:** Verifies if a raw string matches a stored hash with a given salt.
    -   `verify_hash(raw_string, stored_hash, stored_salt)`: Compares the generated hash with the stored hash.
-   **Lambda Version:** A more compact but less readable version using lambda functions was also provided.

## Graph Set for File Relations (NetworkX)

-   Uses the `networkx` library to represent and analyze file relations.
-   `FileRelationsGraph` class:
    -   `add_file_relation(file1, file2)`: Adds an edge between two files.
    -   `visualize_graph()`: Visualizes the graph using `matplotlib.pyplot`.

## Tools to Parse Text and Execute Instructions

-   A Python class `TextParserExecutor` that uses regular expressions (`re`) for text parsing and `subprocess` for command execution.
-   **Security Warning:** Emphasizes the security risks of executing arbitrary commands and the need for input validation and sanitization.

## Pillow Library Use Cases (Image Processing for ML)

-   Pillow (PIL Fork) is used for image processing tasks, especially in machine learning.
-   **Use Cases:**
    -   **Data Preprocessing:** Resizing, cropping, normalization, augmentation.
    -   **Dataset Preparation:** Converting file formats, creating thumbnails.
    -   **Visualization:** Displaying images, overlaying annotations.
    -   **Image Filtering and Feature Extraction:** Applying filters, extracting regions of interest.
    -   **Data Augmentation:** Rotation, flipping, random transformations.
    -   **Integration with Deep Learning Frameworks:** Converting to NumPy arrays.
-   **Examples:** Resizing and normalizing an image, generating images from ML output (e.g., random pixels), generating white noise images.

## Python `bcrypt`

-   A library for hashing passwords using the bcrypt algorithm, designed to be slow and resistant to brute-force attacks.
-   `bcrypt.gensalt()`: Generates a random salt.
-   `bcrypt.hashpw(password.encode('utf-8'), salt)`: Hashes the password.
-   `bcrypt.checkpw(entered_password.encode('utf-8'), hashed_password)`: Verifies a password.

## Python Model for API Gateway (Flask and FastAPI)

-   **Concept:** Designing the structure and functionality of an API gateway to handle requests, route to services, and manage API lifecycle.
-   **Flask Example:** Basic routes for users (`/users`, `/users/<int:user_id>`) using `Flask` and `jsonify`.
-   **FastAPI Example:** Modern, fast web framework for building APIs with Python 3.7+.
    -   Uses `FastAPI` class and `@app.get` decorator.
    -   Example routes for users.
    -   **Multi-API Gateways:** Structuring with `APIRouter` for different functionalities or versions (e.g., `/v1`, `/v2`).
    -   **Calling API inside API:** Using `httpx` for asynchronous HTTP requests to external APIs within a FastAPI route.

## Related Documents

- [[30-All-Notes/Python_Markdown_Files_Organized.md]]
