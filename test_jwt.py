import time
import jwt

# GitHub App credentials
app_id = "1202295"
private_key = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAsrVnUedPHxSFi0NrKZMYHn4b6gYuKk8aTOFVy7t6NvmVTIGi
W/h3wRdL88fEiGU+sD3YyAwRSlRW+IZNVI6gOaLZypsJOlR8FRh1IHuuseswbOBS
jXsdw65bVZ0NRb92y9x875lgdVkKTsvRny6h30T7YXA2ldxHQwK01G9DCyP0Anct
obV+bm3rOzvLkl2YLWkGyU5eT9j4ieMF1KRHXczNHYZLHIFnTXgxhtApzK8RTpH6
QwJ2zxWm16ny2Ppm3YjTbnsAsQDeKjF1E7bBEohiOV3LVLTpSsMnlMwSU30+f23K
pXzVjln+LoUlMv1lB4CamWCkpFhRUujHa+IHLQIDAQABAoIBAB3LzylBxthoxIde
u0xYQSo8Xo0bcLEPNVRiMbrhTFREMtdpuddZyyW/q6M+yI7xSo16El3wXSWmgEW5
psUVbrONaoC0bspx8apWxJig5pS1oQJWOI1sXJ8WwBW7NM5PSRBed9o/GW0XZneS
1iWTUdv3FW6+letQqfULS3kr/+KoWZNbXYHNKg0smzfvNRPwLz0UrUaZjZng6c7S
dJW5IFRg9vRNyMtWPKvtfa4DDFG/7mcjptRcH8SYgYXMOCBxq/BnhhAyjQV3nT+f
Ij9eTHYxIqGwOkLcZdSCQZk3/N/5D6mBwTMxlZYX05e9EVgWq1MZ7m5SQz1uXZUw
JVQhAgECgYEA2FhdmKPTVdKYvjdD/DYfV8jYQ/mUCWUKcVBLiUYjYMHKJXD9aVLJ
fZVm4/fXKIHa+XLzn2ixZYRpHgLvYGHBYFQPwifHOGFca8LSXwXWLXJlXa+zVBEu
lQUP9EBEWlF8UQO4/LRGLXXxpIA+jXAUdlXcUQJB0vVWohC+cgMJSdECgYEA0+Ks
8OlEGRLfGGMGmYRy0CbFVJKVzL0RgYZEPOx5MN4eSKJQRFNzODQNkWnpLHYadBJb
0C9ROTmXdwxiTlfnIiSzBZYyn8TJdL4euvXHSTXwQpZZ2ZfSzKFHJITYb9+Z/xE9
bGSOMQZCbcclLLnBVkDCbG5XreBbDJKgKoVrKU0CgYEAqghfQfss4Xv5FYVBcwjQ
EhZwJcA5RKVvXxDO5iqHFUF7vjICKUqA/Y0QAKAZOkV6DHHWYVKPMbCHHJOTpKkO
KHJpA7RVFQHFvKqCdnpKlRJLQHkxPbFYvYRhzDwGKLUVNw6SicYzZfPRLWnxypVv
mJnMXl4cre8WUlpxGRUJXBECgYBfVE+TFUTRW4AECgYUZ8QJVnJKdXKFjJ8inAWy
KGpBbUFLMxDMOXy9tKI2QQKVdoMxvMJqMDVcXF8gxiGo8JjIVFhzt6Q4zFnYSUQP
XYKTGjYeLQHbFGHgXaV9Sw9QBzO9LowdOD5UcOZ4hRRKpKLjVEOsAIHFo+XKIcxf
AJZ6Q3+3IQKBgHjaDjvgh898xZXTEHQTvj8ldHgNUJcgRvIlHxLFPDGFMIx3qZR0
PYJxKF+3aYMwyTfVISgm8XzVUkhrQbXkCGUTg8U9JLEpwGkxVjxmrIBGkw9iYyMH
yHDJkEXJBYQx5lnIY8fKLdLQJjgYmXWO/5FTnSFY1xQECPzDJGKhkgQH
-----END RSA PRIVATE KEY-----"""

print(f"App ID: {app_id}")
print(f"Private key length: {len(private_key)}")

try:
    # Create a JWT for GitHub App authentication
    now = int(time.time())
    payload = {
        "iat": now,
        "exp": now + 600,  # 10 minutes expiration
        "iss": app_id
    }
    
    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
    print(f"JWT created successfully: {encoded_jwt[:20]}...")
    print("Test passed!")
except Exception as e:
    print(f"Error creating JWT: {str(e)}")
    import traceback
    traceback.print_exc()
