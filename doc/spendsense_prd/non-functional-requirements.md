# Non-Functional Requirements

## Performance
- Page load time: <2s on 4G connection
- API response time: <500ms for 95th percentile
- Feature computation: <5s per user
- Chat response: <3s

## Security
- All data encrypted in transit (HTTPS/TLS)
- All data encrypted at rest (RDS encryption, S3 encryption)
- JWT tokens for authentication (AWS Cognito)
- Application-layer security (data access enforced in application code - users can only access their own data, operators can access all data based on role)
- No PII in logs or decision traces
- Rate limiting on all endpoints (API Gateway)
- CORS configured for frontend domain only

## Scalability
- MVP targets 100 concurrent users
- Database can handle 1000 users with current schema
- Background jobs isolated from request path
- Horizontal scaling possible (stateless API)

## Reliability
- 99% uptime target for MVP demo period
- Automated health checks
- Error logging to Sentry or similar
- Database automated backups daily

## Accessibility
- WCAG 2.1 AA compliance target
- Keyboard navigation support
- Screen reader friendly
- Color contrast ratios meet standards

---
