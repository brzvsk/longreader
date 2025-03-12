# Authentication Documentation

This document describes the authentication process for the Longreader application using Telegram WebApp.

## Telegram WebApp Integration

- The application integrates with Telegram's WebApp platform, allowing users to authenticate using their Telegram account.
- The application must be opened within Telegram's WebApp environment to function properly.

## Authentication Flow

1. **Initial Check:**
   - When the application loads, it checks for the presence of the Telegram WebApp environment.
   - If not running within Telegram WebApp, an error is shown: "This app must be opened in Telegram".

2. **User Authentication:**
   - The application automatically receives user data from Telegram WebApp's `initData`.
   - This data includes user information and a hash for verification.
   - The raw `initData` is sent to the backend for validation and user creation/retrieval.

3. **Data Validation:**
   - The server verifies the hash using the Bot API token to ensure data integrity.
   - The validation follows Telegram's official [data validation process](https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app).

4. **User Management:**
   - Upon successful validation, the server either retrieves an existing user or creates a new one.
   - User data is stored in MongoDB with the following structure:
     ```typescript
     interface User {
         id: string;              // MongoDB ObjectId
         telegram_id: string;     // Telegram user ID
         metadata: {
             registered_at: Date;
             referral?: string;
         };
     }
     ```

## REST API Endpoints

Described in [API docs](API.md)

## Client-Side Authentication

The frontend manages authentication state using:

1. **Local Storage:**
   - `user_id`: MongoDB user ID
   - `telegram_id`: Telegram user ID

2. **Auth Context:**
   - Provides authentication state to the entire application
   - Manages loading and error states
   - Automatically initiates authentication on application load

## Security Considerations

- The Bot API token is kept secure on the server side and never exposed to clients.
- All authentication data is validated using Telegram's cryptographic hash verification.
- User sessions are managed through secure storage of user IDs.
- The application must be served over HTTPS to ensure data security.
