# Access Control (Reserved Design)

**Status: not implemented, on purpose.** The site is public by default and hidden from search engines only (`X-Robots-Tag: noindex, nofollow`, see `gotchas.md#noindex-instead-of-robots`). This file records how to make it private if a site ever needs it, so the decision does not have to be worked out again. Check the Cloudflare dashboard names against the current Cloudflare docs before following it: the UI moves.

---

## 1. Why public is the default

The site exists to be read by AI agents as much as by people:

- The **AI Reader** link under every H1 hands a public chatbot (Claude, ChatGPT, Gemini) the URL `<site>/p/<doc_id>.md`. The chatbot fetches it from its own servers, without the reader's login.
- **`llms.txt`** and the `p/<doc_id>.md` files are fetched the same way by agents' web fetch tools, which cannot sign in and cannot add custom headers.

Behind a login, both stop working for everyone who is not a signed-in browser. So privacy is a trade: turn it on only when the content must not be public, and accept losing these two features for outside chatbots.

---

## 2. The design: Cloudflare Zero Trust, e-mail one-time PIN

Cloudflare Access (part of Cloudflare Zero Trust) sits in front of the Pages site. No code in this repository changes; the build and deploy stay the same.

| Part | Choice | Why |
| :--- | :--- | :--- |
| Login method | **One-time PIN**: the reader types an e-mail address, Cloudflare mails a code, the reader types the code | No identity provider to set up, no passwords to manage |
| Who may enter | An **allow-list of e-mail addresses** (or a whole e-mail domain) in an Allow policy | A code is only sent to listed addresses |
| What is protected | One Access application for the production host (`<project>.pages.dev`, and the custom domain if there is one), one for the preview hosts (`*.<project>.pages.dev`) | Preview deployments are full copies of the site |
| Agents of the owner | A **service token** with a Service Auth policy on the same application | Scripts send `CF-Access-Client-Id` and `CF-Access-Client-Secret` headers, no browser |
| Session | The default session length; shorten it for sensitive content | One code per session, not per page |
| Search engines | Keep the `noindex` headers | Harmless, and still right if Access is ever turned off |

Cost: the Zero Trust free plan covers a small team; check the current seat limit before relying on it.

---

## 3. Steps, when a site needs it

All of these change an external service: the user runs them, or approves each one.

1. **Zero Trust organization.** In the Cloudflare dashboard open Zero Trust and create the team (organization) once per account.
2. **Login method.** Settings > Authentication: make sure One-time PIN is enabled.
3. **Application.** Access > Applications > Add > Self-hosted. Domain: `<project>.pages.dev` (and the custom domain). Add a second application for `*.<project>.pages.dev`, or turn on the Pages project's built-in access policy for preview deployments.
4. **Allow policy.** Action Allow, Include: Emails (the allow-list) or Emails ending in (`@<domain>`).
5. **Service token for agents (optional).** Access > Service Auth > Create service token, then add a policy with Action Service Auth that includes that token. Store the client ID and secret in the local secret store, never in the repository.
6. **Check.** In a private window the site asks for an e-mail and a code; `curl -I <site>/llms.txt` without headers no longer returns the file; with the two service token headers it does.

To automate later: a `setup-cloudflare-access` mise task can create the applications and policies through the Cloudflare API, idempotently, like `setup-cloudflare-secrets`. Its API token needs the Access: Apps and Policies Edit permission, which the Pages upload token does not have. It is an external-service task: run only after the user's yes.

---

## 4. What changes on a private site

- **AI Reader link.** Public chatbots get the login page instead of the text. Either remove the link (stop inserting it in the Sphinx extension) or change its label to say it only works for a chatbot that can sign in.
- **`llms.txt` and `p/<doc_id>.md`.** Only clients with the service token can read them. A query skill or script that reads the site must send the two headers with `curl`; an agent's built-in web fetch tool cannot.
- **Nothing else.** `_headers`, `_redirects`, `404.html`, Pagefind search and the build are unchanged: Access only decides who reaches the site.

Do not try to keep `llms.txt` or `/p/*` public with a Bypass policy on a private site: those paths hold the full text of every document, so the site would not be private.
