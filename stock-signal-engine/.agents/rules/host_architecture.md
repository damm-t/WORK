# Host Architecture & Machine Roles

- **24/7 Production Host**: The trading engine runs 24/7 on a dedicated Windows machine (`seesharpwin1`) at Tailscale IP `100.105.70.120`. It runs all 4 desks (Stocks, Crypto, Futures, Forex) and the FastAPI webapp on port 8080.
- **Local Mac (`macbook-pro`)**: This Mac is a development/client machine, NOT the 24/7 server. The user can close the lid, shut down, or let the Mac sleep at any time without stopping the bot.
- **Remote Mobile Access**: The user views the dashboard and HUD widget from their phone over Tailscale at `http://100.105.70.120:8080/widget`.
- **Do NOT Run Duplicate Bot on Mac**: Never launch duplicate background autopilots (`./quant start`) on this Mac unless explicitly debugging, to prevent conflicting orders with the 24/7 Windows host.
