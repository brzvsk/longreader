# Article Management Service API

This document describes the REST API for the Article Management Service, which handles operations related to articles in the Longreader application.

## Base URL
`https://api.longreader.com/v1`

## Endpoints

### Create Article

- **Endpoint:** `/article`
- **Method:** `POST`
- **Description:** Create a new article by providing all necessary fields. The service will store the content.
- **Request Body:**
  ```json
  {
    "url": "string",
    "title": "string",
    "source": "string",
    "readingTime": "integer",
    "progress": {
      "percentage": "integer"
    }
  }
  ```
- **Response:**
  - **201 Created**
    ```json
    {
      "id": "string",
      "title": "string",
      "source": "string",
      "readingTime": "integer",
      "progress": {
        "percentage": "integer"
      }
    }
    ```
  - **400 Bad Request** - Invalid data or missing parameters.

### Get Article

- **Endpoint:** `/articles/{id}`
- **Method:** `GET`
- **Description:** Retrieve the content and metadata of a specific article.
- **Response:**
  - **200 OK**
    ```json
    {
      "id": "string",
      "title": "string",
      "content": "string",
      "source": "string",
      "readingTime": "integer",
      "progress": {
        "percentage": "integer"
      }
    }
    ```
  - **404 Not Found** - Article not found.

### Update Article

- **Endpoint:** `/article/{id}`
- **Method:** `PUT`
- **Description:** Update article details such as reading progress or annotations.
- **Request Body:**
  ```json
  {
    "progress": "integer",
    "annotations": "string"
  }
  ```
- **Response:**
  - **200 OK** - Article updated successfully.
  - **400 Bad Request** - Invalid data provided.
  - **404 Not Found** - Article not found.

### Delete Article

- **Endpoint:** `/article/{id}`
- **Method:** `DELETE`
- **Description:** Soft delete an article. The article can be recovered from the recently deleted view.
- **Response:**
  - **204 No Content** - Article deleted successfully.
  - **404 Not Found** - Article not found.

### List Articles

- **Endpoint:** `/articles`
- **Method:** `GET`
- **Description:** Retrieve a list of all articles with optional filters for sorting and status.
- **Query Parameters:**
  - `status` (optional): `read`, `unread`, `archived`
  - `sort` (optional): `date`, `progress`
- **Response:**
  - **200 OK**
    ```json
    [
      {
        "id": "string",
        "title": "string",
        "source": "string",
        "readingTime": "integer",
        "progress": {
          "percentage": "integer"
        }
      }
    ]
    ```

## Error Handling

- **400 Bad Request:** Invalid input or parameters.
- **404 Not Found:** Resource not found.
- **500 Internal Server Error:** Unexpected server error.

## Authentication

- The Article Management Service API uses Telegram WebApp authentication. For detailed implementation, refer to the [Authentication Documentation](./Authentication.md).