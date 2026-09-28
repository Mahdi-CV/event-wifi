# Security

This project controls network interfaces and uses Jupyter credentials. Treat
configuration and result artifacts accordingly.

- Never commit Wi-Fi PSKs, API tokens, cookies, private URLs, or attendee data.
- Use a dedicated, short-lived, least-privilege Jupyter test credential.
- Keep `config/wifi.env` mode `0600`.
- Run only against networks and services you are authorized to test.
- Review JSONL output before sharing; kernel output and network details may be
  sensitive.
- Rotate credentials immediately if they appear in Git history or test logs.

Report security issues privately to the repository owner rather than opening a
public issue containing credentials or infrastructure details.

