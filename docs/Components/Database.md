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
│       "_id": "telegramUserId",
│       "metadata": {
│           "registeredAt": "date",
│           "referral": "string"
│       }
│   }
├── articles
│   └── {
│       "_id": "articleId",
│       "title": "string",
│       "content": "string",
│       "shortDescription": "string",
│       "metadata": {
│           "sourceUrl": "string",
│           "author": "string",
│           "publishDate": "date",
│           "readingTime": "number"
│       },
│       "createdAt": "date"
│   }
└── userArticles
    └── {
        "_id": "ua123",
        "userId": "telegramUserId",
        "articleId": "articleId",
        "progress": {
            "percentage": "number",
            "lastPosition": "number",
            "updatedAt": "date"
        },
        "timestamps": {
            "savedAt": "date",
            "archivedAt": "date",
            "deletedAt": "date"
        }
    }
```

