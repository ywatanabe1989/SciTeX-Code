<!-- ---
!-- Timestamp: 2025-08-01 00:49:16
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/docs/from_user/crawl4ai.md
!-- --- -->

# https://github.com/unclecode/crawl4ai

docker pull unclecode/crawl4ai:latest
docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g unclecode/crawl4ai:latest

# Visit the playground at http://localhost:11235/playground

<!-- EOF -->