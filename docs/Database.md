# Database Structure

This document describes the database organization for the Longreader Telegram Bot. We use MongoDB as our primary database system.

## Overview

The database is organized into several collections to support article management, user progress tracking, and gamification features in future.

## Data Model Design Rationale

Articles can exist independently of users, allowing **multiple users to reference the same article** without duplicating content. This is particularly important for popular articles that many users might save, and unlocks sharing of articles between users.

The `userArticles` collection serves as a junction table, managing the many-to-many relationship between users and articles while storing user-specific data like reading progress and highlights.

```
LongreaderDB
├── users
│   └── {
│       "_id": "ObjectId",
│       "telegram_id": "string",  # Using string to handle large telegram IDs safely
│       "metadata": {
│           "registered_at": "datetime",
│           "referral": "string?"
│       }
│   }
├── articles
│   └── {
│       "_id": "ObjectId",
│       "title": "string",
│       "content": "string?",
│       "short_description": "string",
│       "metadata": {
│           "source_url": "string",
│           "author": "string?",
│           "publish_date": "datetime?",
│           "reading_time": "number?"
│       },
│       "created_at": "datetime"
│   }
└── userArticles
    └── {
        "_id": "ObjectId",
        "user_id": "ObjectId",
        "article_id": "ObjectId",
        "progress": {
            "percentage": "float",  # defaults to 0
            "last_position": "int",  # defaults to 0
            "updated_at": "datetime?"
        },
        "timestamps": {
            "saved_at": "datetime?",
            "archived_at": "datetime?",
            "deleted_at": "datetime?"
        }
    }
```

### Database Indexes

The following indexes are maintained for optimal query performance:

- **articles collection**:
  - `created_at`

- **user_articles collection**:
  - `user_id`
  - `(user_id, article_id)` (unique compound index)
  - `timestamps.saved_at`

- **users collection**:
  - `telegram_id` (unique)
  - `metadata.registered_at`
