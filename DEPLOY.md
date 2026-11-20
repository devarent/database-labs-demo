# Deploy Database Labs Demo

The app is a single container plus PostgreSQL. Any host that can run a Dockerfile or a Python 3.12 process can run it. This guide covers the four paths that are practical for a portfolio demo.

> Prices and free-tier limits change. Verify the current terms on each provider before you rely on them.

## Before you deploy

1. Change the local database password. The Compose default (`labpassword`) is not a deployment secret.
2. Generate a strong password and URL-encode it if it contains `@`, `:`, `/`, or `?`.
3. Keep `.env` out of git. Every platform below injects environment variables instead.
4. Decide whether the demo is read-only. A public write endpoint will be found and abused; see [Public demo hardening](#public-demo-hardening).

## Option A: Render blueprint

`render.yaml` creates a free web service and a free PostgreSQL database.

1. Push this repository to GitHub.
2. In Render, choose **New > Blueprint** and connect the repository.
3. Apply the blueprint. Render creates `database-labs-db` and `database-labs-demo`.
4. Wait for the health check at `/healthz` to pass.
5. Open the service URL.

Notes:

- Render's free web service spins down after inactivity; the first request is slow.
- The free PostgreSQL plan is time-limited. When it expires, create a Neon or Supabase database and set `DATABASE_URL` manually. Remove the `databases` block from `render.yaml` first.
- To use an external database now, replace the `fromDatabase` block with:

  ```yaml
  envVars:
    - key: DATABASE_URL
      sync: false
  ```

  Then paste the connection string in the Render dashboard.

## Option B: Fly.io

```bash
fly auth login
fly launch --no-deploy --name <unique-app-name>
fly postgres create --name database-labs-db --region sin
fly postgres attach database-labs-db --app <unique-app-name>
fly deploy
fly open
```

`fly postgres attach` sets a `DATABASE_URL` secret. The app rewrites `postgres://` to `postgresql+psycopg://` automatically.

The included `fly.toml` scales to zero:

```toml
auto_stop_machines = "stop"
auto_start_machines = true
min_machines_running = 0
```

The trade-off is a cold start after idle periods. Set `min_machines_running = 1` if you need an always-warm demo, and check the cost.

Fly Postgres is an app you own, not a fully managed service. Back it up before upgrades.

## Option C: VPS + Caddy

This is the cheapest always-on option and the one that gives you the most control.

### 1. Provision

- Ubuntu 24.04 LTS, 1–2 vCPU, 1–2 GB RAM, 20 GB disk.
- Create a non-root user with SSH keys.
- Point a DNS `A` record at the VPS, for example `demo.example.com`.

### 2. Install Docker

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker "$USER"
```

Log out and back in.

### 3. Firewall

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

Do **not** open 5433 or 8080. Compose binds both to `127.0.0.1`.

### 4. Run the stack

```bash
git clone https://github.com/devarent/database-labs-demo.git
cd database-labs-demo
printf 'POSTGRES_PASSWORD=%s\n' "$(openssl rand -base64 24)" > .env
docker compose up -d --build
curl -fsS http://127.0.0.1:8080/healthz
```

### 5. Caddy with TLS and basic auth

```bash
sudo apt-get install -y caddy
caddy hash-password --plaintext 'choose-a-long-password'
```

`/etc/caddy/Caddyfile`:

```caddyfile
demo.example.com {
    basicauth {
        demo <paste-the-bcrypt-hash>
    }
    reverse_proxy 127.0.0.1:8080
}
```

```bash
sudo systemctl reload caddy
```

Caddy obtains a certificate automatically. Only 80/443 are public.

### 6. Verify

From your laptop:

```bash
curl -I https://demo.example.com
nmap -Pn -p- <vps-ip>
```

Only 22, 80, and 443 should be open. On the VPS, `ss -tulpn` should show the app and database on `127.0.0.1`, not `0.0.0.0`.

## Option D: Neon or Supabase + any app host

Neon and Supabase both offer free PostgreSQL tiers. This is the best path if you do not want to operate a database.

1. Create a project and copy the **pooled** connection string.
2. URL-encode the password if needed.
3. Set `DATABASE_URL` on your app host. For example:

   ```text
   postgresql+psycopg://user:password@host/dbname?sslmode=require
   ```

4. Deploy the Docker image anywhere: Render, Fly, Railway, Koyeb, or a VPS.
5. Run the app once so it creates and seeds the table.

Neon scales to zero; the first query after idle can be slow. Supabase's free tier may pause inactive projects.

## Public demo hardening

If you want recruiters to use the demo without a VPN:

- Put only the HTTP UI behind TLS. Never expose PostgreSQL.
- Add basic auth at the proxy, or an auth layer in the app.
- Consider disabling `POST` and `DELETE` for the public instance with a read-only flag.
- Use a dedicated database and a dedicated user with minimal privileges.
- Set a request rate limit at the proxy.
- Add a budget alert.
- Tear the demo down when the application window closes.

The current app has no authentication. That is fine behind a tunnel or basic auth; it is not fine as an open write endpoint on the public internet.

## Backups

### Docker Compose

```bash
docker compose exec -T db pg_dump -U lab -d labs -Fc > labs-$(date +%F).dump
```

Restore:

```bash
cat labs-2026-01-01.dump | docker compose exec -T db pg_restore -U lab -d labs --clean --if-exists
```

### Managed providers

Enable automated backups and point-in-time recovery where the plan allows it. Test a restore before you need it.

## Post-deploy checklist

- [ ] `GET /healthz` returns `{"status":"ok"}`.
- [ ] The UI loads with 26 seed rows.
- [ ] Adding an engine survives a page refresh.
- [ ] Deleting the test row works.
- [ ] The database port is not reachable from the internet.
- [ ] TLS is valid and HTTP redirects to HTTPS.
- [ ] `.env` and platform secrets are not in git.
- [ ] A backup or snapshot exists.
- [ ] A billing or usage alert is configured.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| `/healthz` returns 503 | `docker compose logs db`; confirm the password and `DATABASE_URL`. |
| `connection refused` on 5433 | The `db` container is not healthy yet; wait for `pg_isready`. |
| `password authentication failed` | The volume was created with a different password. Use `docker compose down -v` for local, or rotate the password. |
| `relation "engines" does not exist` | Startup failed before `create_all`; read the app logs. |
| Special characters in the password break the URL | Percent-encode `@ : / ? #` in `DATABASE_URL`. |
| Render/Fly cannot connect | Use the platform's internal connection string, not `localhost`. |
| Free instance is slow on first request | Expected with scale-to-zero; warm it or pay for an always-on instance. |

## Cost sketch

| Path | Typical cost | Trade-off |
| --- | --- | --- |
| Render free | $0 | Spins down; free database is time-limited |
| Fly scale-to-zero | Usage-based, small | Cold starts; you own the Postgres app |
| VPS + Caddy | ~$5–6/month | You patch the OS |
| Neon/Supabase free + small host | $0–5/month | Provider limits and idle pauses |

Check current pricing before you commit.
