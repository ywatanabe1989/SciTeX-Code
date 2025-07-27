<!-- ---
!-- Timestamp: 2025-07-27 12:24:05
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/README.md
!-- --- -->


## Usage

#### OpenAthens
``` bash
python -m scitex.scholar.auth._OpenAthensAuthenticator --email user@university.edu
```

#### Abstracted
``` python
from scitex.scholar.auth import (
    AuthenticationManager,
    OpenAthensAuthenticator,
)

# Create manager
auth_manager= AuthenticationManager()

auth_manager.register_provider("openathens", OpenAthensAuthenticator(
    email="user@university.edu"
))

# Set active provider
auth_manager.set_active_provider("openathens")

# Authenticate
await auth_manager.authenticate()

# Get auth data
cookies = await auth_manager.get_auth_cookies()
headers = await auth_manager.get_auth_headers()

# Check status
is_auth = await auth_manager.is_authenticated()
```

<!-- EOF -->