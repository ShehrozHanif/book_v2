---
name: authentication-ui
description: Create signup/login forms and authentication flow UI components
model: sonnet
---

# Authentication UI Skill

## Purpose
Build secure, user-friendly authentication interface components for signup, login, and credential management.

## Key Responsibilities
- Design signup/login form layouts
- Implement form validation and error handling
- Build password strength indicators
- Create forgot password flows
- Build email verification UI
- Implement OAuth/social login buttons
- Add session management UI
- Build user profile/account settings
- Handle form state and submission

## Form Types

### Login Form
- Email/username input
- Password input with show/hide toggle
- Remember me checkbox
- Login button
- Forgot password link
- Sign up link
- OAuth options

### Signup Form
- Email input with validation
- Password input with strength meter
- Confirm password input
- Terms & conditions checkbox
- Create account button
- Login link
- Optional: phone, name fields

### Password Reset
- Email input for recovery
- Submit button
- Success/error messaging
- Return to login link

### Email Verification
- Verification code input
- Resend code button
- Countdown timer
- Success state

## Form Validation

### Client-Side Rules
```
Email:
- Valid email format
- Not empty

Password:
- Min 8 characters
- Uppercase + lowercase
- Numbers + special chars
- Match confirmation

Username:
- 3-20 characters
- Alphanumeric + underscore
- Unique check
```

## UI Components

### Input Field Component
```jsx
<AuthInput
  label="Email"
  type="email"
  value={email}
  onChange={handleChange}
  error={errors.email}
  placeholder="your@email.com"
  required
/>
```

### Password Strength Indicator
```jsx
<PasswordStrength
  password={password}
  showRules={true}
/>
```

### OAuth Buttons
```jsx
<OAuthButtons
  providers={['google', 'github', 'microsoft']}
/>
```

## Form State Management

```jsx
const [formData, setFormData] = useState({
  email: '',
  password: '',
  confirmPassword: '',
});

const [errors, setErrors] = useState({});
const [loading, setLoading] = useState(false);
const [showPassword, setShowPassword] = useState(false);
```

## Validation Functions

### Email Validation
```jsx
const isValidEmail = (email) => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
};
```

### Password Validation
```jsx
const isStrongPassword = (password) => {
  const minLength = password.length >= 8;
  const hasUppercase = /[A-Z]/.test(password);
  const hasLowercase = /[a-z]/.test(password);
  const hasNumbers = /\d/.test(password);
  const hasSpecial = /[!@#$%^&*]/.test(password);

  return minLength && hasUppercase && hasLowercase &&
         hasNumbers && hasSpecial;
};
```

## Features

### Password Visibility Toggle
- Show/hide icon
- Accessible toggle
- Maintains focus

### Remember Me
- Local storage persistence
- Clear on logout
- Privacy/security warning

### Error Display
- Field-level errors
- Inline error messages
- Clear messaging
- Accessibility (aria-describedby)

### Loading States
- Disabled inputs during submission
- Loading spinner
- Prevent double submission
- Timeout handling

### Session Management
- Login success redirect
- Auto-logout on token expiration
- Session persistence
- Logout confirmation

## Security Considerations
- Never log passwords
- Use HTTPS for credentials
- Implement CSRF protection
- Rate limit login attempts
- Add captcha for security
- Store tokens securely (httpOnly cookies)
- Implement 2FA/MFA support

## Responsive Design
- Mobile-optimized forms
- Touch-friendly inputs
- Proper spacing and sizing
- Keyboard navigation support

## Accessibility Features
- Proper labels for all inputs
- Error messages with ARIA
- Keyboard navigation
- Focus management
- Screen reader support
- Color contrast compliance

## Integration Points
- Connect to authentication API
- Handle JWT tokens
- Manage auth context
- Protected routes
- Redirect after auth success/failure
