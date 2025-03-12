# LongReader API Reference

This document describes the REST API for the LongReader application.

## Base URL
`https://api.longreader.brzv.sk`

## Authentication

All endpoints require authentication via Telegram WebApp. For detailed implementation, refer to the [Authentication Documentation](./Authentication.md).

## API Sections

- [Authentication API](#authentication-api)
- [Article Management API](#article-management-api)
- [User Article Management API](#user-article-management-api)
- [Article Parser API](#article-parser-api)
- [Sharing API](#sharing-api)

## Authentication API

### Authenticate with Telegram

- **Endpoint:** `/auth/telegram`
- **Method:** `POST`
- **Description:** Authenticates a user via Telegram WebApp and returns user identifiers.
- **Request Body:**
  ```json
  {
    "init_data": "string"  // Raw initData from Telegram WebApp
  }
  ```
- **Response:**
  - **200 OK**
    ```json
    {
      "user_id": "string",     // MongoDB user ID
      "telegram_id": "string"  // Telegram user ID
    }
    ```
  - **401 Unauthorized** - Invalid authentication data
  - **422 Unprocessable Entity** - Invalid user data format

## Article Management API

### Create Article

- **Endpoint:** `/articles`
- **Method:** `POST`
- **Description:** Create a new article by providing all necessary fields.
- **Request Body:**
  ```json
  {
    "url": "string",
    "title": "string",
    "content": "string",
    "short_description": "string",
    "metadata": {
      "source_url": "string",
      "author": "string",
      "publish_date": "string",
      "reading_time": "integer"
    }
  }
  ```
- **Response:**
  - **201 Created**
    ```json
    {
      "id": "string",
      "title": "string",
      "short_description": "string",
      "metadata": {
        "source_url": "string",
        "author": "string",
        "publish_date": "string",
        "reading_time": "integer"
      }
    }
    ```
  - **400 Bad Request** - Invalid data or missing parameters

### Get Article

- **Endpoint:** `/articles/{id}`
- **Method:** `GET`
- **Description:** Retrieve an article by ID without user context
- **Response:**
  - **200 OK**
    ```json
    {
      "id": "string",
      "title": "string",
      "content": "string",
      "short_description": "string",
      "metadata": {
        "source_url": "string",
        "author": "string",
        "publish_date": "string",
        "reading_time": "integer"
      }
    }
    ```
  - **404 Not Found** - Article not found

## User Article Management API

### List User Articles

- **Endpoint:** `/users/{user_id}/articles`
- **Method:** `GET`
- **Description:** Retrieve all articles saved by a user in a flattened structure (without content)
- **Response:**
  - **200 OK**
    ```json
    {
      "articles": [
        {
          "id": "string",
          "title": "string",
          "short_description": "string",
          "metadata": {
            "source_url": "string",
            "author": "string",
            "publish_date": "string",
            "reading_time": "integer"
          },
          "progress": {
            "percentage": "float",
            "last_position": "integer",
            "updated_at": "string"
          },
          "timestamps": {
            "saved_at": "string",
            "archived_at": "string",
            "deleted_at": "string"
          }
        }
      ]
    }
    ```

### Get User Article

- **Endpoint:** `/users/{user_id}/articles/{article_id}`
- **Method:** `GET`
- **Description:** Get a specific article with user context
- **Response:**
  - **200 OK** - Same as List User Articles response, but includes the article `content` field
  - **404 Not Found** - Article not found for user

### Update Article Progress

- **Endpoint:** `/users/{user_id}/articles/{article_id}/progress`
- **Method:** `PUT`
- **Description:** Update reading progress for a user's article
- **Query Parameters:**
  - `progress_percentage`: float (0-100)
- **Response:**
  - **200 OK** - Updated article with new progress
  - **404 Not Found** - Article not found for user

### Archive Article

- **Endpoint:** `/users/{user_id}/articles/{article_id}/archive`
- **Method:** `PUT`
- **Description:** Archive an article for a user
- **Response:**
  - **200 OK** - Updated article with archived status
  - **404 Not Found** - Article not found for user

### Unarchive Article

- **Endpoint:** `/users/{user_id}/articles/{article_id}/unarchive`
- **Method:** `PUT`
- **Description:** Unarchive an article for a user
- **Response:**
  - **200 OK** - Updated article with unarchived status
  - **404 Not Found** - Article not found for user

### Delete Article

- **Endpoint:** `/users/{user_id}/articles/{article_id}`
- **Method:** `DELETE`
- **Description:** Soft delete an article for a user
- **Response:**
  - **204 No Content** - Article deleted successfully
  - **404 Not Found** - Article not found for user

### Check Article Status

- **Endpoint:** `/users/{user_id}/articles/{article_id}/status`
- **Method:** `GET`
- **Description:** Check if an article is new, saved, or deleted for a user
- **Response:**
  - **200 OK**
    ```json
    {
      "status": "string"  // "new" | "saved" | "deleted"
    }
    ```

## Article Parser API

### Parse Article

- **Endpoint:** `/users/{telegram_user_id}/articles/parse`
- **Method:** `POST`
- **Description:** Parse article from URL and create user-article link
- **Request Body:**
  ```json
  {
    "url": "string"
  }
  ```
- **Response:**
  - **200 OK** - Parsed article data
  - **500 Internal Server Error** - Failed to parse article

## Sharing API

### Create Share Message

- **Endpoint:** `/users/{user_id}/articles/{article_id}/share`
- **Method:** `POST`
- **Description:** Creates a prepared inline message for sharing an article via Telegram
- **Parameters:**
  - `user_id`: User's ID
  - `article_id`: Article's ID to share
- **Response:**
  - **200 OK**
    ```json
    {
      "message_id": "string"  // Telegram prepared message ID
    }
    ```
  - **404 Not Found** - User not found or Telegram ID not available
  - **500 Internal Server Error** - Failed to create share message

## Error Handling

All endpoints may return these error responses:

- **400 Bad Request** - Invalid input or parameters
- **401 Unauthorized** - Invalid or missing authentication
- **404 Not Found** - Resource not found
- **500 Internal Server Error** - Unexpected server error

## Rate Limiting

The API implements article parsing limits:

- **Daily Article Limit:** Users can parse up to 10 articles per day (configurable via `DAILY_ARTICLE_LIMIT` environment variable)
- The limit is checked when parsing new articles via `/users/{telegram_user_id}/articles/parse`
- When the limit is exceeded, the API returns:
  - Status code: `429 Too Many Requests`
  - Error message: "Daily article limit exceeded. You can parse up to {limit} articles per day."

Note: Rate limits are not enforced in test environment (when `TELEGRAM_BOT_ENVIRONMENT=test`).