# Node.js API Template

This template provides a fully configured Node.js API with Express and TypeScript.

## Features

- Express server with TypeScript
- Environment variable support with dotenv
- ESLint and Prettier configuration
- Nodemon for development
- TS-Node for direct TypeScript execution
- Basic API routes and middleware
- Error handling
- CORS support

## Project Structure

```
src/
├── controllers/
├── middleware/
├── routes/
├── utils/
├── types/
├── app.ts
└── server.ts
```

## Getting Started

```bash
npm install
npm run dev
```

## Available Scripts

- `npm run dev` - Start development server with nodemon
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier
