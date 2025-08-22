<div align="center">
  <h1 style="font-size: 3em; font-weight: 900; letter-spacing: -0.05em;">ARKHEION-X</h1>
  <p style="font-size: 1.25em;">
    <strong>An open-source framework for autonomous digital entities, focused on decentralized threat & alpha intelligence.</strong>
  </p>
</div>

<p align="center">
    <a href="https://github.com/Yudis-bit/Arkheion-X/actions/workflows/sentinel_patrol.yml"><img src="https://img.shields.io/github/actions/workflow/status/Yudis-bit/Arkheion-X/sentinel_patrol.yml?style=flat-square&logo=githubactions&logoColor=white&label=Vektor%20Sentinel" alt="Vektor Sentinel Status"></a>
    <a href="https://github.com/Yudis-bit/Arkheion-X/stargazers"><img src="https://img.shields.io/github/stars/Yudis-bit/Arkheion-X?style=flat-square&logo=github&color=blue" alt="GitHub Stars"></a>
    <a href="https://github.com/Yudis-bit/Arkheion-X/blob/master/LICENSE"><img src="https://img.shields.io/github/license/Yudis-bit/Arkheion-X?style=flat-square" alt="License"></a>
    <a href="https://twitter.com/ArkheionX"><img src="https://img.shields.io/twitter/follow/arkheionx?style=flat-square&logo=x&label=Follow" alt="Follow on X"></a>
</p>

<p align="center">
  <a href="#what-is-arkheion-x"><strong>What is ARKHEION-X?</strong></a> ·
  <a href="#active-modules"><strong>Modules</strong></a> ·
  <a href="#getting-started"><strong>Getting Started</strong></a> ·
  <a href="#join-the-mission"><strong>Contribute</strong></a>
</p>

---

<div align="center">
  ![ARKHEION-X Quant Engine Dashboard Demo](URL_GIF_DEMO_ANDA_DI_SINI)
</div>

---

## What is ARKHEION-X?

**ARKHEION-X** is an open-core framework for building and deploying autonomous agents that provide an asymmetric advantage in hostile digital environments. We operate at the intersection of cybersecurity, quantitative analysis, and decentralized systems.

Our mission is to democratize access to high-fidelity intelligence, building tools that are traditionally reserved for hedge funds and nation-state actors, and making them available to individual developers and small teams.

-   **Unified Intelligence:** Combines off-chain (code analysis) and on-chain (transactional analysis) data streams into a single, correlated intelligence picture.
-   **Autonomous by Design:** Our agents are built to be deployed and operate 24/7 with minimal human intervention.
-   **Radical Transparency:** The core engines are 100% open-source. We believe trust is earned through verifiable code, not marketing claims.
-   **High-Performance:** Built with efficient, modern tech stacks (Node.js & Python) to ensure speed and reliability.

## Active Modules

The framework is composed of several specialized, interoperable modules.

### Vektor Sentinel `[STATUS: AUTONOMOUS]`
A real-time software supply chain threat hunter. Vektor Sentinel autonomously patrols the NPM registry via a decentralized cron job (GitHub Actions), identifies potential typosquatting attacks, and broadcasts alerts.

*Example Alert Output:*
```json
{
  "SIG-TYPE": "Typosquatting",
  "TARGET": "express-session-validator",
  "MIMICS": "express-session",
  "CONFIDENCE": "HIGH (dist: 1)"
}
```

### Quant Engine `[STATUS: FUNCTIONAL PROTOTYPE]`
An alpha-intel engine that detects "smart money" movements on-chain. By tracking significant transfers and identifying fresh wallets funded by major exchanges, it aims to generate pre-narrative alpha signals.

*Example Signal Output:*
```json
{
  "signal_type": "Fresh Wallet Accumulation",
  "token": "ARB",
  "to": "0x51C7...a7F",
  "amount": "11,766.96",
  "receiver_tx_count": 1,
  "confidence": "CRITICAL"
}
```

## Getting Started (Running Quant Engine Locally)

You can run the Quant Engine prototype on your local machine in under 5 minutes.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Yudis-bit/Arkheion-X.git](https://github.com/Yudis-bit/Arkheion-X.git)
    cd Arkheion-X
    ```

2.  **Setup the Python Environment:**
    ```bash
    # Navigate to the module
    cd modules/quant-engine

    # Create and activate virtual environment
    python -m venv venv
    source venv/Scripts/activate

    # Install dependencies
    pip install -r requirements.txt
    ```

3.  **Configure your `.env` file:**
    Create a `.env` file inside `modules/quant-engine/` and add your RPC URL and GitHub PAT.
    ```
    ARBITRUM_RPC_URL="YOUR_RPC_URL"
    GITHUB_PAT="YOUR_GITHUB_PAT"
    ```

4.  **Run the Unified System:**
    Navigate back to the root directory and run the main controller.
    ```bash
    cd ../.. 
    python main.py
    ```
    This will launch all agents concurrently. To view the data, run the dashboard in a separate terminal: `streamlit run modules/quant-engine/dashboard.py`.

## Join the Mission

ARKHEION-X is currently built and maintained by a solo operator. The project's strength comes from community feedback and validation.

-   Got an idea or found a bug? **[Open an Issue](https://github.com/Yudis-bit/Arkheion-X/issues)**.
-   Want to discuss strategy? **[Start a Discussion](https://github.com/Yudis-bit/Arkheion-X/discussions)**.

Our long-term vision is to build a decentralized network of intelligence agents. This is just the beginning.