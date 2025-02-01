# Core Features Description

## Article Management

### List of Articles
- Display saved articles in a scrollable list
- Show article title, source, estimated reading time, reading progress
- Support sorting by date added, group by source/author
- Quick actions: archive, delete, continue reading
- Visual indicators for read/unread status

### Article Reading
- Clean, distraction-free reading interface
- Text formatting preservation from original article
- Adjustable text size and font
- Dark/light mode support
- Progress bar showing reading position
- Auto-save reading position
- Offline reading support

### Reading Progress
- Track reading progress per article for each user
- Resume from last read position
- Progress statistics:
  - Percentage completed
  - Time spent reading
  - Reading speed metrics
- Sync progress across devices

### Article Management
#### Archiving
- Move completed articles to archive
- Archive browsing with filters
- Option to unarchive
- Bulk archive actions

#### Delete Function
- Remove articles from library
- Confirmation dialog
- Bulk delete option
- Recently deleted recovery (30 days)

## Parser Integration
- Support for major news sites and blogs
- Clean content extraction
- Metadata preservation
- Error handling for invalid URLs
- Background processing for large articles
- Progress indication during parsing

Implementation of the Parser microservice is described in the [Parser Documentation](../Components/Parser.md).


## Frontend Requirements

### 1. Article List UI
- [ ] Scrollable list of saved articles
- [x] Article cards with:
  - Title, source, reading time
  - Progress indicator
  - Quick action buttons
- [ ] Read/unread status indicators
- [ ] Sort controls
- [ ] Group by source/author
- [ ] Archive list

### 2. Reading Interface
- [ ] Clean article view
- [ ] Text formatting
  - Font size controls
  - Dark/light mode toggle
- [x] Progress bar
- [ ] Bottom action buttons:
  - Share
  - Archive
- [x] Resume position on open

### 3. Article Management UI
- [ ] Archive/Unarchive controls
- [ ] Delete functionality
- [ ] Bulk action controls
- [ ] Recently deleted view
- [ ] Confirmation dialogs

### 4. Statistics display
- [ ] Completion percentage
- [ ] Time spent
- [ ] Reading speed

## Backend Requirements

### 1. Authentication

Description of the Authentication is available in the [Authentication Documentation](../Components/Authentication.md).

### 2. Article Management

Backend serves as a REST API server for the frontend and article management service: CRUD operations, authentication, and communication with the parser service.

API reference is available in the [Article Management API Documentation](../Components/ArticleManagementAPI.md).

Technical details are available in the [Backend Implementation Documentation](../Components/BackendImplementation.md).

<details>
  <summary>Article Management Service requirements</summary>
  <ul>
    <li>Create
      <ul>
        <li>Call parser service</li>
        <li>Create article record</li>
        <li>Handle background jobs</li>
        <li>Track parsing status</li>
        <li>Return article data</li>
      </ul>
    </li>
    <li>Read
      <ul>
        <li>Article content retrieval</li>
        <li>Reading position tracking</li>
        <li>Progress calculation</li>
        <li>Statistics aggregation</li>
      </ul>
    </li>
    <li>Update
      <ul>
        <li>Content refresh</li>
        <li>Reading progress sync</li>
        <li>Archive status changes</li>
        <li>User annotations</li>
      </ul>
    </li>
    <li>Delete
      <ul>
        <li>Soft deletion</li>
        <li>Hard deletion</li>
        <li>Batch operations</li>
        <li>Cleanup jobs</li>
      </ul>
    </li>
  </ul>
</details>

### 3. Parser

Separate microservice is used for parsing articles. Operates in background and returns parsed data to the article management service. Utilizes open-source [Trafilatura](https://github.com/adbar/trafilatura) library.

Description is available in the [Parser Documentation](../Components/Parser.md).

### 4. Frontend Implementation

Serves as a frontend for the Telegram WebApp. Next.js is used as a framework. Utilizes [Shadcn UI](https://ui.shadcn.com/) library.

Description is available in the [Frontend Implementation Documentation](../Components/FrontendImplementation.md).

### 5. Telegram Bot Handler

Serves as a Telegram bot handler. Utilizes [Telegram Bot API](https://core.telegram.org/bots/api) and [Telegram WebApp](https://core.telegram.org/bots/webapps).