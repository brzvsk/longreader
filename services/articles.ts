import { Article, ArticleContent } from "@/types/article"

// This will be replaced with actual API call in the future
export async function getArticles(): Promise<Article[]> {
  // Simulate API call
  await new Promise((resolve) => setTimeout(resolve, 700))
  
  return [
    {
      id: "1",
      title: "Understanding React Server Components",
      description: "A deep dive into React Server Components and how they change the way we build React applications.",
      source: "dev.to",
      author: "reactdev",
      readingTimeMinutes: 8,
      readingProgress: 20,
      savedAt: "2024-03-15T10:00:00Z",
      thumbnailUrl: "https://picsum.photos/seed/1/800/600",
      sourceIconUrl: "https://picsum.photos/seed/1/800/600",
    },
    {
      id: "2",
      title: "The Future of Web Development with Next.js 15",
      description: "Exploring the latest features and improvements in Next.js 15 and what they mean for developers.",
      source: "medium.com",
      readingTimeMinutes: 12,
      readingProgress: 65,
      savedAt: "2024-03-14T15:30:00Z",
      thumbnailUrl: "https://picsum.photos/seed/2/800/600",
    //   sourceIconUrl: "https://picsum.photos/seed/2/800/600",
    },
  ]
}

const articles: Record<string, ArticleContent> = {
  "1": {
    id: "1",
    title: "Understanding React Server Components",
    content: `
# Understanding React Server Components

React Server Components represent a paradigm shift in how we build React applications. They provide a new way to think about component rendering and data fetching.

## What are Server Components?

Server Components are components that execute and render on the server. Unlike traditional React components, they never run on the client, which brings several advantages:

- Direct database access
- Reduced client-side JavaScript
- Improved initial page load

## Key Benefits

### 1. Performance
Server Components can access data sources directly without additional network requests. This means faster page loads and reduced client-side processing.

### 2. Security
Sensitive operations can be performed entirely on the server, keeping API keys and other credentials secure.

### 3. Bundle Size
By executing on the server, these components don't contribute to the JavaScript bundle sent to clients.

## Code Example

\`\`\`jsx
async function BlogPost({ id }) {
  const post = await db.posts.findById(id);
  return (
    <article>
      <h1>{post.title}</h1>
      <p>{post.content}</p>
    </article>
  );
}
\`\`\`

## Conclusion

Server Components are changing how we think about React applications, bringing the best of server-side rendering while maintaining React's component model.
    `,
    author: "reactdev",
    source: "dev.to",
    readingTimeMinutes: 8,
    readingProgress: 20,
    savedAt: "2024-03-15T10:00:00Z",
    thumbnailUrl: "https://picsum.photos/seed/1/800/600",
  },
  "2": {
    id: "2",
    title: "The Future of Web Development with Next.js 15",
    content: `
# The Future of Web Development with Next.js 15

Next.js 15 brings groundbreaking improvements to the developer experience and application performance. Let's explore what's new and how it changes web development.

## Major Improvements

### 1. Turbopack
The new Rust-based bundler promises significantly faster build times and improved development experience.

### 2. Server Actions
Built-in solution for handling form submissions and mutations without API routes.

### 3. Partial Prerendering
Combine static and dynamic content seamlessly in the same page.

## Performance Enhancements

Next.js 15 focuses heavily on performance optimizations:

- Improved static optimization
- Better code splitting
- Enhanced image optimization
- Smarter client-side caching

## Developer Experience

The developer experience has been significantly improved:

\`\`\`typescript
// New API design
export default async function Page() {
  const data = await db.query()
  
  return (
    <main>
      <h1>Welcome to Next.js 15</h1>
      {data.map(item => (
        <Card key={item.id} {...item} />
      ))}
    </main>
  )
}
\`\`\`

## Looking Forward

The future of web development with Next.js 15 looks promising, with more features planned for upcoming releases.
    `,
    author: undefined,
    source: "medium.com",
    readingTimeMinutes: 12,
    readingProgress: 65,
    savedAt: "2024-03-14T15:30:00Z",
    thumbnailUrl: "https://picsum.photos/seed/2/800/600",
  }
}

export async function getArticleById(id: string): Promise<ArticleContent> {
  await new Promise((resolve) => setTimeout(resolve, 500))
  
  const article = articles[id]
  if (!article) {
    throw new Error('Article not found')
  }
  
  return article
} 