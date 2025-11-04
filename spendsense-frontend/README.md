# SpendSense Frontend

React + TypeScript + Vite frontend application for the SpendSense financial education platform.

## Prerequisites

- Node.js 18+ and npm
- AWS CLI configured (for accessing AWS resources)

## Setup

1. **Install dependencies:**

   ```bash
   npm install
   ```

2. **Configure environment variables:**

   Copy `.env.example` to `.env.local` and update with your values:

   ```bash
   cp .env.example .env.local
   ```

   Edit `.env.local` with your configuration:
   - `VITE_API_URL`: Backend API URL (default: `http://localhost:8000` for local development)
   - `VITE_COGNITO_USER_POOL_ID`: AWS Cognito User Pool ID
   - `VITE_COGNITO_CLIENT_ID`: AWS Cognito Client ID

   **Getting AWS Resource Values:**

   To get Cognito values from AWS CDK stack outputs:
   ```bash
   # User Pool ID
   aws cloudformation describe-stacks \
     --stack-name SpendSense-Cognito-dev \
     --query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' \
     --output text

   # Client ID
   aws cloudformation describe-stacks \
     --stack-name SpendSense-Cognito-dev \
     --query 'Stacks[0].Outputs[?OutputKey==`UserPoolClientId`].OutputValue' \
     --output text
   ```

   Or from AWS Secrets Manager:
   ```bash
   aws secretsmanager get-secret-value \
     --secret-id spendsense/cognito/configuration \
     --query SecretString \
     --output text | jq -r '.user_pool_id'
   ```

3. **Run the development server:**

   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173` (or the port shown in the terminal)

4. **Run tests:**

   ```bash
   npm test
   ```

## Environment Variables

Vite automatically loads `.env.local` file in development mode. Only variables prefixed with `VITE_` are exposed to client-side code.

**Accessing Environment Variables in Code:**

```typescript
// Environment variables are accessible via import.meta.env
const apiUrl = import.meta.env.VITE_API_URL
const cognitoUserPoolId = import.meta.env.VITE_COGNITO_USER_POOL_ID
const cognitoClientId = import.meta.env.VITE_COGNITO_CLIENT_ID
```

**Important Notes:**
- `.env.local` is gitignored - never commit actual secrets
- Variables are replaced at build time, not runtime
- `.env.local` takes precedence over `.env` files
- For production builds, set environment variables in your deployment environment

## AWS Credentials

For local development, you need AWS credentials configured. Options:

1. **AWS CLI credentials file** (recommended):
   ```bash
   aws configure
   ```
   This creates `~/.aws/credentials` and `~/.aws/config`

2. **Environment variables**:
   ```bash
   export AWS_ACCESS_KEY_ID=your-access-key
   export AWS_SECRET_ACCESS_KEY=your-secret-key
   export AWS_REGION=us-east-1
   ```

3. **AWS SSO/Profiles**:
   ```bash
   aws configure sso
   aws sso login --profile your-profile
   ```

## Project Structure

```
spendsense-frontend/
├── src/
│   ├── components/      # React components
│   ├── features/        # Feature modules
│   ├── lib/             # Utilities and helpers
│   └── main.tsx         # Application entry point
├── .env.local           # Local environment variables (gitignored)
├── .env.example         # Environment variables template
└── vite.config.ts       # Vite configuration
```

## Development

- **Formatting**: Prettier (configured)
- **Linting**: ESLint (configured)
- **Testing**: Vitest
- **Type Checking**: TypeScript

---

# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
