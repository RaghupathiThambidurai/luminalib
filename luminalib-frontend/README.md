# LuminalLib Frontend

Modern Next.js 16 application with **React 19**, **TypeScript 5**, and **Tailwind CSS 4**.

## 🚀 Quick Start (30 seconds)

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

✅ App ready at `http://localhost:3000`

---

## 🔑 Authentication

**Test Credentials:**
```
Username: testuser
Password: password123
```

The authentication hook (`useAuth`) automatically:
- Stores JWT token in `localStorage`
- Includes token in API requests
- Handles token refresh
- Logs out on token expiry

---

## 🏠 Pages Overview

### Public Pages
- `/` - Home page
- `/auth/login` - Login form
- `/auth/signup` - Registration form

### Protected Pages (Require Login)
- `/books` - Book listing & search
- `/books/[id]` - Book details + reviews + sentiment analysis
- `/profile` - User profile
- `/reviews` - User's reviews

---

## 📁 Project Structure

```
luminalib-frontend/
├── app/                          # Next.js App Router
│   ├── page.tsx                  # Home page
│   ├── layout.tsx                # Root layout
│   ├── globals.css               # Global styles
│   ├── providers.tsx             # Context providers
│   │
│   ├── auth/
│   │   ├── login/page.tsx        # Login form
│   │   └── signup/page.tsx       # Registration form
│   │
│   ├── books/
│   │   ├── page.tsx              # Book listing
│   │   ├── [id]/page.tsx         # Book details & reviews
│   │   └── upload/page.tsx       # Upload book (admin)
│   │
│   ├── profile/page.tsx          # User profile
│   └── reviews/page.tsx          # User's reviews
│
├── components/                    # Reusable React components
│   ├── Alerts.tsx                # Alert component
│   ├── Button.tsx                # Button component
│   └── Card.tsx                  # Card component
│
├── hooks/                         # Custom React hooks
│   ├── useAuth.ts                # Authentication state
│   └── useAsync.ts               # Async data fetching
│
├── lib/
│   └── api-client.ts             # API communication
│
├── types/
│   └── index.ts                  # TypeScript types
│
├── public/                        # Static assets
├── package.json
├── tsconfig.json
├── next.config.ts
├── tailwind.config.ts
└── jest.config.js
```

---

## 🔌 API Integration

### API Client (`lib/api-client.ts`)

```typescript
import { apiClient } from '@/lib/api-client';

// Automatically includes JWT token in headers
const response = await apiClient.post('/api/books/book-1/reviews', {
  rating: 5,
  content: 'Great book!'
});
```

### useAuth Hook (`hooks/useAuth.ts`)

```typescript
import { useAuth } from '@/hooks/useAuth';

export default function MyComponent() {
  const { user, login, logout, isAuthenticated } = useAuth();
  
  if (!isAuthenticated) return <div>Please login</div>;
  
  return <div>Welcome, {user?.username}</div>;
}
```

### useAsync Hook (`hooks/useAsync.ts`)

```typescript
import { useAsync } from '@/hooks/useAsync';

export default function BookList() {
  const { data: books, loading, error } = useAsync(
    () => apiClient.get('/api/books'),
    []
  );
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return <div>{books.map(b => <div key={b.id}>{b.title}</div>)}</div>;
}
```

---

## 🎨 Styling with Tailwind

All components use **Tailwind CSS 4**:

```tsx
// Input field (login page)
<input
  type="password"
  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
  placeholder="Password"
/>

// Button
<button className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">
  Login
</button>

// Card
<div className="bg-white rounded-lg shadow-md p-4">
  <h2 className="text-xl font-bold">Card Title</h2>
</div>
```

---

## 📋 Key Features

### Authentication
- ✅ JWT token management
- ✅ Secure login/signup
- ✅ Auto token refresh
- ✅ Logout support
- ✅ Protected routes

### Book Management
- ✅ List all books
- ✅ Search & filter
- ✅ View book details
- ✅ Upload books (admin)
- ✅ Book images

### Reviews with AI Sentiment
- ✅ Submit review with rating
- ✅ View all reviews for book
- ✅ Mark reviews helpful/unhelpful
- ✅ **Sentiment score displayed** (from backend)
- ✅ Real-time sentiment analysis

### User Profile
- ✅ View profile info
- ✅ See my reviews
- ✅ Edit profile (ready to implement)

---

## 🧪 Testing

### Login Flow
```typescript
// Navigate to http://localhost:3000/auth/login
// Enter: testuser / password123
// Click Login
// Should redirect to /books
```

### Submit Review with Sentiment
```typescript
// Navigate to book details page
// Scroll to "Leave a Review" section
// Fill in rating & comment
// Submit review
// Backend analyzes sentiment automatically
// Check database for sentiment_score
```

### API Testing
```bash
# Get JWT token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# Use token in frontend API calls
# (useAuth hook handles this automatically)
```

---

## 🏗️ Component Examples

### Login Form (`app/auth/login/page.tsx`)
```tsx
export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuth();
  
  async function handleLogin() {
    await login(username, password);
    // Redirect handled by hook
  }
  
  return (
    <div className="max-w-md mx-auto">
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        className="w-full px-4 py-2 text-black border rounded-lg"
        placeholder="Username"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="w-full px-4 py-2 text-black border rounded-lg mt-4"
        placeholder="Password"
      />
      <button
        onClick={handleLogin}
        className="w-full bg-blue-600 text-white py-2 rounded-lg mt-4"
      >
        Login
      </button>
    </div>
  );
}
```

### Book Details with Reviews (`app/books/[id]/page.tsx`)
```tsx
export default function BookDetailPage({ params }: { params: { id: string } }) {
  const { data: book } = useAsync(() => apiClient.get(`/api/books/${params.id}`), []);
  const { data: reviews } = useAsync(() => apiClient.get(`/api/books/${params.id}/reviews`), []);
  
  async function handleReviewSubmit(rating: number, content: string) {
    await apiClient.post(`/api/books/${params.id}/reviews`, {
      rating,
      content
    });
    // Sentiment analysis happens automatically on backend
  }
  
  return (
    <div>
      <h1>{book?.title}</h1>
      <p>{book?.description}</p>
      
      <h2>Reviews</h2>
      {reviews?.map(review => (
        <div key={review.id} className="bg-white rounded-lg p-4 mb-4">
          <p>Rating: {review.rating}/5</p>
          <p>{review.content}</p>
          <p className="text-sm text-gray-600">
            Sentiment Score: {review.sentiment_score?.toFixed(2)}
          </p>
        </div>
      ))}
      
      <ReviewForm onSubmit={handleReviewSubmit} />
    </div>
  );
}
```

---

## 🔧 Configuration

### Environment Variables

Create `.env.local`:
```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional
NEXT_PUBLIC_APP_NAME=LuminalLib
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### TypeScript Configuration (`tsconfig.json`)
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "jsx": "preserve",
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

---

## 🧯 Troubleshooting

### "Cannot find module '@/...'"
- Check `tsconfig.json` paths configuration
- Ensure files exist in correct locations
- Restart dev server

### Login not working
- Ensure backend is running on `http://localhost:8000`
- Check credentials: testuser / password123
- Check browser DevTools → Network tab for API calls
- Check backend logs for errors

### Sentiment score showing as null
- Backend is analyzing sentiment asynchronously
- Check backend logs: "✅ Analyzed review {id}"
- Refresh page after 1-2 seconds
- Verify LLM provider is configured in backend

### Styles not applied (Tailwind)
- Ensure Tailwind CSS is imported in `app/globals.css`
- Check `tailwind.config.ts` includes app/ directory
- Restart dev server after config changes
- Check for typos in class names

---

## 📦 Build & Deployment

### Production Build
```bash
# Build optimized version
npm run build

# Start production server
npm run start
```

### Deployment to Vercel
```bash
# Vercel auto-deploys from GitHub
# Or use Vercel CLI:
npm install -g vercel
vercel
```

### Docker Deployment
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

```bash
docker build -t luminallib-frontend .
docker run -p 3000:3000 luminallib-frontend
```

---

## ✅ Features Implemented

- ✅ Next.js 16 with App Router
- ✅ React 19 functional components
- ✅ TypeScript 5 type safety
- ✅ Tailwind CSS 4 styling
- ✅ JWT authentication
- ✅ Protected routes
- ✅ API integration
- ✅ Book listing & details
- ✅ Review submission
- ✅ Sentiment score display
- ✅ User profile
- ✅ Responsive design
- ✅ Form validation
- ✅ Error handling
- ✅ Loading states

---

## 🚀 Next Steps

### Immediate
1. [ ] Start dev server: `npm run dev`
2. [ ] Login with testuser / password123
3. [ ] Browse books
4. [ ] Submit a review
5. [ ] Watch sentiment analysis work

### Short Term
1. [ ] Add book search filters
2. [ ] Implement profile editing
3. [ ] Add book favorites/wishlist
4. [ ] Improve UI/UX design

### Long Term
1. [ ] User recommendations
2. [ ] Social features (follow users)
3. [ ] Advanced search
4. [ ] Admin dashboard
5. [ ] Dark mode toggle

---

## 📚 Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

---

## 🎯 Quick Commands

```bash
# Development
npm run dev        # Start dev server (http://localhost:3000)
npm run build      # Create production build
npm run start      # Start production server
npm run lint       # Run ESLint
npm test           # Run Jest tests

# Dependencies
npm install        # Install all dependencies
npm update         # Update dependencies
npm outdated       # Check for outdated packages
```

---

**Backend API:** `http://localhost:8000`
**Frontend:** `http://localhost:3000`
**Swagger Docs:** `http://localhost:8000/docs`
