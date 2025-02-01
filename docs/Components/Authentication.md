# Authentication Documentation

This document describes the authentication process for the Longreader application using Telegram WebApp.

## Telegram WebApp Integration

- The application integrates with Telegram's WebApp platform, allowing users to authenticate using their Telegram account.

## Authentication Flow

1. **User Login:**
   - When a user accesses the application, they are prompted to log in via Telegram.
   - Upon successful login, Telegram provides a WebApp data object containing user information and a hash for verification.

2. **Token Generation:**
   - The server verifies the hash using the Bot API token to ensure the data's integrity and authenticity. [Learn more about verifying data authenticity](https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app)
   - Once verified, the server generates a session token for the user, which is used for subsequent API requests.

## REST API Endpoints

### Login

- **Endpoint:** `/auth/login`
- **Method:** `POST`
- **Description:** Authenticates a user via Telegram WebApp and generates a session token.
- **Request Body:**
  ```json
  {
    "telegramData": "object"
  }
  ```
- **Response:**
  - **200 OK**
    ```json
    {
      "sessionToken": "string"
    }
    ```
  - **400 Bad Request** - Invalid Telegram data.

### Logout

- **Endpoint:** `/auth/logout`
- **Method:** `POST`
- **Description:** Invalidates the user's session token, effectively logging them out.
- **Request Body:**
  ```json
  {
    "sessionToken": "string"
  }
  ```
- **Response:**
  - **204 No Content** - Logout successful.
  - **401 Unauthorized** - Invalid or expired session token.

## Authorization Header

- All API requests must include the session token in the `Authorization` header as a Bearer token:
  ```
  Authorization: Bearer {session_token}
  ```

## Session Management

- The server manages user sessions, ensuring tokens are valid and not expired.
- Users can log out, which invalidates the session token.

## Security Considerations

- Ensure the Bot API token is kept secure and not exposed in client-side code.
- Use HTTPS to encrypt data in transit, protecting user credentials and session tokens.

This authentication method leverages Telegram's secure platform, providing a seamless and secure login experience for users.
