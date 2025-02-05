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

# MongoDB vs PostgreSQL Comparison

| Feature/Aspect                  | MongoDB                                                                 | PostgreSQL                                                              |
|---------------------------------|-------------------------------------------------------------------------|-------------------------------------------------------------------------|
| **Schema Flexibility**          | ✅ Allows easy evolution without migrations                              | ❌ Requires migrations for schema changes                               |
| **Developer Experience (Python)**| ✅ Great integration with Motor and FastAPI                              | ❌ More complex ORM setup required                                      |
| **Developer Experience (Kotlin)**| 😐 KMongo provides idiomatic API but with type safety challenges         | ❌ More complex ORM setup required                                      |
| **Performance for Read-Heavy Workloads** | ✅ Efficient for retrieving full articles with related data          | ✅ Good performance for complex queries                                 |
| **Multi-Language Support**      | ✅ Native drivers for both Python and Kotlin                             | ✅ Native drivers available                                             |
| **Transaction Support**         | ❌ Limited ACID transactions                                             | ✅ Full ACID compliance                                                 |
| **Storage Space Efficiency**    | ❌ Document repetition might use more storage                            | ✅ More efficient with proper normalization                             |
| **Complex Queries**             | 😐 Requires aggregation framework for join-like operations               | ✅ Better for complex analytical queries                                |
| **Integration Complexity**      | 😐 `_id` field as `ObjectId` adds complexity in Python                   | ❌ Requires SQL schema maintenance                                      |
| **Data Consistency**            | 😐 Ensuring consistency across collections can be challenging            | ✅ Better data integrity guarantees                                     |

### Key Points

- **Schema Flexibility**: MongoDB offers greater flexibility, allowing for easy evolution of the data model without migrations.
- **Developer Experience**: MongoDB integrates well with Python and provides a more idiomatic API for Kotlin, though there are challenges with type safety and complex queries.
- **Performance**: Both databases perform well for read-heavy workloads, but MongoDB is particularly efficient for retrieving full articles with all related data.
- **Transaction Support**: PostgreSQL provides full ACID compliance, offering better data integrity guarantees.
- **Storage Efficiency**: PostgreSQL is more efficient with storage due to proper normalization.
- **Complex Queries**: PostgreSQL excels in handling complex analytical queries and aggregation capabilities.
- **Integration Complexity**: MongoDB's `_id` field and multi-collection queries can add complexity, especially in Python applications.
- **Storing Full Articles in PostgreSQL**: 
  - **Advantages**: Supports large text fields, offers full-text search, and maintains relational integrity with strong consistency.
  - **Challenges**: Schema rigidity requires migrations for changes, potential performance impact for large text retrievals, and less flexibility compared to MongoDB's document model.

### Recommendation by GPT

Given the application's requirements:
1. Document-oriented data model for articles
2. FastAPI and Kotlin tech stack
3. Read-heavy workload
4. Need for schema flexibility

MongoDB is the recommended choice. The document model naturally fits the article storage requirements, provides excellent integration with the chosen tech stack, and offers better flexibility for future feature additions. While PostgreSQL offers stronger ACID compliance and complex query capabilities, these advantages are less critical for the current feature set of the reading-focused application.

