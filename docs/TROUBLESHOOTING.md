# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the GitHub Review Agent.

## Common Issues

### Authentication Errors

#### Issue: "Invalid token" or "Unauthorized"

- **Cause**: Invalid or expired GitHub token
- **Solution**:
  1. Verify token in `.env` file
  2. Check token permissions on GitHub
  3. Generate new token if expired
  4. Ensure token has required scopes:
     - `repo`
     - `workflow`
     - `read:org`

#### Issue: "Repository access denied"

- **Cause**: Insufficient repository permissions
- **Solution**:
  1. Check repository access settings
  2. Verify organization permissions
  3. Request access from repository admin

### Installation Problems

#### Issue: Dependencies installation fails

- **Cause**: Python version mismatch or missing system packages
- **Solution**:

  1. Verify Python version (3.8+)
  
    ```bash
    python --version
    ```

  2. Update pip

    ```bash
    python -m pip install --upgrade pip
    ```

  3. Install system dependencies

  ```bash
  # Ubuntu/Debian
  sudo apt-get update
  sudo apt-get install python3-dev

  # macOS
  brew install python3
  ```

#### Issue: Configuration file not found
- **Cause**: Missing or misplaced .env file
- **Solution**:
  1. Check if `.env` exists in config directory
  2. Copy from example:
  ```bash
  cp config/.env.example config/.env
  ```
  3. Verify file permissions
  ```bash
  chmod 600 config/.env
  ```

### Runtime Issues

#### Issue: Review process hangs
- **Cause**: API rate limits or network issues
- **Solution**:
  1. Check GitHub API rate limits
  2. Verify network connectivity
  3. Check logs for timeout errors
  ```bash
  tail -f logs/review-agent.log
  ```
  4. Increase timeout settings in config

#### Issue: False positives in reviews
- **Cause**: Overly strict rule configuration
- **Solution**:
  1. Review rule settings in config
  2. Adjust threshold values
  3. Disable problematic rules
  4. Create rule exceptions

### Integration Issues

#### Issue: Webhook delivery failures
- **Cause**: Misconfigured webhook or network issues
- **Solution**:
  1. Verify webhook URL
  2. Check webhook logs
  3. Validate payload signature
  4. Test webhook endpoint:
  ```bash
  curl -X POST -H "Content-Type: application/json" \
    -d '{"test": true}' https://your-webhook-url
  ```

#### Issue: CI/CD Integration fails
- **Cause**: Pipeline configuration issues
- **Solution**:
  1. Check CI/CD logs
  2. Verify environment variables
  3. Test integration locally
  4. Update pipeline configuration

## Logging and Debugging

### Enable Debug Logging

1. Set log level in `.env`:
```
LOG_LEVEL=DEBUG
```

2. View detailed logs:
```bash
tail -f logs/review-agent.log
```

### Common Log Messages

```
ERROR: Failed to authenticate - Invalid token
```
➤ Check token configuration

```
WARNING: Rate limit approaching
```
➤ Reduce request frequency or upgrade plan

```
ERROR: Repository not found
```
➤ Verify repository exists and is accessible

## Performance Optimization

### Slow Reviews

1. Check system resources:
```bash
top  # or htop
```

2. Monitor memory usage:
```bash
ps aux | grep review-agent
```

3. Optimize configuration:
- Reduce concurrent reviews
- Adjust timeout settings
- Enable caching

### High Resource Usage

1. Check review queue size
2. Monitor system metrics
3. Adjust worker pool size
4. Enable rate limiting

## Maintenance

### Regular Health Checks

1. Monitor disk space:
```bash
df -h
```

2. Check log rotation:
```bash
ls -l logs/
```

3. Verify backup status
4. Test recovery procedures

### Updates and Upgrades

1. Update dependencies:
```bash
pip install -r requirements.txt --upgrade
```

2. Check for new releases:
```bash
git fetch origin
git tag -l
```

3. Backup before upgrading:
```bash
cp -r config config.backup
```

## FAQ

**Q: How do I reset the review agent?**
A: Stop the service, clear cache, restart:
```bash
systemctl stop review-agent
rm -rf /tmp/review-agent/*
systemctl start review-agent
```

**Q: Where are the logs stored?**
A: Default location: `logs/review-agent.log`

**Q: How do I change review sensitivity?**
A: Adjust thresholds in configuration file

## Getting Help

If issues persist:

1. Check [GitHub Issues](https://github.com/Roxonn-FutureTech/github-review-agent/issues)
2. Join [Discord Community](https://discord.gg/github-review-agent)
3. Email Support: support@roxonn-futuretech.com

Include when seeking help:
- Error messages
- Log excerpts
- Configuration files
- Steps to reproduce