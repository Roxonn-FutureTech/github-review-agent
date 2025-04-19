import jwt
import time

# GitHub App credentials
app_id = "1202295"
private_key = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA6XtOXx5cZgRXm5xyQQoL9XJE/og9otiKvQnzLsWY/LyhFP8J
NkXXRjyKxITzjYNtlzCbHfwGxPahbLZCR+1KUKlE8kThQbZUYUCQRJJiKdF8B5Ek
LVuIJYbKMhxPJeK9TKbLUwMwdKt0YPTBcXUlT7DP6c5Hn2JVpj1/UcCvM8pk/DFg
Tf5Bh/YqM+yyJIWcnMaIjT6YlLrLSFwdFRYiDWLcv4uL2iUG2zMqxUY0EBTJFPHn
LYEXzgGvAXgFW5KFOuLHdvQKojpDXWEVZUh5iUCPl5YMwtUjKJGnNHxEUgfyHU+L
NxWJEpUTgHEnTzNxP9nJVKEICQyFqyJbx8fQDQIDAQABAoIBAQCxCCC/0xgTgEZS
KHAUGYYFBJYTKBmN0+30UcKSYlYyNKkXQHJZUVdFAkn5XCMMGr6yGGH5jWGY+Dzx
YDCiGTmH5qE5dBXiHAJsAGQgG/MQz+/8UNgbYdRQjTP5ULhUkZ0PKY7Mxl+FdPdO
xnKEepuKfLo4ORgAGt7EZb3RQV8fbVTPVmkKTKzSgKFNwqwNROKOYBZCXGJgwuGG
QK0Vn1OvGEODAGTta7+p9JIEtgbQCldNdmQiZzJbGrBvZG5KlsqLGmGIcwRcmHYY
Yxl2SYJLxzbpAKV0zRONTDJ+aNTSVLmOBOvCBhV9Mdsc2MpjkbsLDyH6v9eTBTK+
F4ZLBgYBAoGBAPxbqUgEQPi9lnIKHN0q7NF8RxGXI3MJmSl6nIFvVs9qMFsYFhRr
QMS5zUKfYH0R3QKWfx8JJe3IpfR0SxkUKxGp7TL8jALArVB7F6xNH8IQA8/e5Ncn
rKKvS+vZPZ9cZ4Qj/LnXEjswJxJrZP6B3KEy5CYlDQNqJKjPi4qS2XnNAoGBAOzs
fyo+y2a7KwjTgwFpNJQVuTwwyfFnXUwPs8Qe7c/6S5jTdYdl+TAQpkGnrURyUiQF
HnCEGRMvqz2R4AEhLb6XoXhvQcAFLpZsUKfTJZ9XQ0YFOUmCYA9DgVhwjzSRnVZ4
QiyVG/SgRXfMfwXjR0nZL83Oau0r9jX7MwzPsJsBAoGAcJBxwUlMPYFVYLzjEQQs
0qXgztz/JG85VwoBzlhPBFsslmC5UHQcUDW/WG+QZmrMnfCvmBQWJ7kmpKvP5PcH
fcIe889YCsVUGqmqQtCFGJqwjVsP5HWncX0dK+/9aXeJNGWsvLGGiGYzEPXKJvwf
HGIXwR7VLVNzFQQKDzZ5JlUCgYEAkSjgBfqbOvrh8qMjIrjGd2qGHLqUGyOYzpIJ
Jpj3n+v9E5BRVnZ+O0WJ0/2lxGVmOGCPClXrSKQA0/+0jEWoyy5PBvJcG9Rn3Woe
AXuhGfSr6LOQSQJnxzJjXidCR/M+dJ70xI+Mpb+n+jVBJJKLuPi3KgdL8QYI+Smm
OQBLfAECgYBJrfpgQQPZZfQxrxjr7s8Tc24P6jh2l5XdxhQJRq7BGbXC9+jXjBSi
PHlhvpEiLyLlmandYJsJKfD4+HLTWPwNyEH8eQTNBcA/xmG9BVJYeZ8YOcwLr5ZQ
xjEVyXXnc+JYJq4wHJ48hZKJRYKXWYTJzT/+BC5dXG4QUeEBnuCYJA==
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
    
    # Try with different algorithms
    algorithms = ["RS256", "RS384", "RS512"]
    
    for algorithm in algorithms:
        try:
            print(f"\nTrying algorithm: {algorithm}")
            encoded_jwt = jwt.encode(payload, private_key, algorithm=algorithm)
            print(f"✅ JWT created successfully with {algorithm}: {encoded_jwt[:20]}...")
        except Exception as e:
            print(f"❌ Failed with {algorithm}: {str(e)}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
