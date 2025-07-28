# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.6.x   | :white_check_mark: |
| 0.5.x   | :white_check_mark: |
| < 0.5   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in OpenSuperWhisper, please report it to us by:

1. **Creating a private security advisory** on GitHub
2. **Emailing** the maintainer directly (if contact info is available)

Please **do not** create a public issue for security vulnerabilities.

## Security Considerations

### API Key Storage
- API keys are stored locally using Qt's QSettings (Windows Registry on Windows)
- Keys are stored in plaintext - consider this when using on shared systems
- We recommend using environment variables in production environments

### Audio Data
- Audio recordings are temporarily stored locally during processing
- Temporary files are automatically cleaned up after processing
- No audio data is permanently stored by default

### Network Security
- All API calls use HTTPS encryption
- OpenAI API keys are transmitted securely
- No user data is collected or transmitted beyond OpenAI API usage

## Best Practices

1. **Protect your API key**: Never share or commit API keys to version control
2. **Monitor usage**: Regularly check your OpenAI usage dashboard
3. **Use environment variables**: For production/server deployments
4. **Keep updated**: Update to the latest version for security patches