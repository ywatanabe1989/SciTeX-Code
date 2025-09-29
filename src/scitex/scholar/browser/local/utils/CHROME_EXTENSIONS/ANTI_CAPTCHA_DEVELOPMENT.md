<!-- ---
!-- Timestamp: 2025-08-01 19:19:05
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/local/ANTI_CAPTCHA_DEVELOPMENT.md
!-- --- -->


# Anti-Captcha Development Resources

## Summary: Install these two chrome extensions
[2Captcha](https://2captcha.com/captcha-bypass-extension)
[CAPTCHA Solver](https://chromewebstore.google.com/detail/captcha-solver-auto-hcapt/hlifkpholllijblknnmbfagnkjneagid)

## Captcha Services and Test Sites

1. Google reCAPTCHA - 75-80% market share
   - v2
     - https://www.google.com/recaptcha/api2/demo (v2 demo)
   - v3
     - https://recaptcha-demo.appspot.com/recaptcha-v3-request-scores.php
   - v2, v3, Enterprise versions
   - Solved by [2Captcha](https://2captcha.com/captcha-bypass-extension)

2. hCaptcha - 15-20% market share
   - https://accounts.hcaptcha.com/demo
   - Growing rapidly, privacy-focused alternative
   - Partially solved by [CAPTCHA Solver](https://chromewebstore.google.com/detail/captcha-solver-auto-hcapt/hlifkpholllijblknnmbfagnkjneagid)

3. Cloudflare Turnstile - 3-5% market share
   - not working 
     - https://httpbin.org/status/403
     - https://demo.turnstile.worker_asyncs.dev/
     - https://turnstile.example.com/
   - https://developers.cloudflare.com/turnstile/get-started/client-side-rendering/

   - Newest player, launched 2022

4. FunCaptcha (Arkose Labs) - 1-2% market share
   - https://captcha.com/demos/features/captcha-demo.aspx
   - Enterprise-focused, gaming/interactive challenges

5. reCAPTCHA v3 Testing
   - Score testing system

<!-- EOF -->