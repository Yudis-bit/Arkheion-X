// =============================================================================
// == VEKTOR SENTINEL v0.4.3
// == CONSOLIDATED POLLING & BROADCASTING ENGINE (COMPONENT UPGRADE)
// == AUTHOR: ARKHEION-X HYPEROPS
// =============================================================================

// --- PHASE 1: DEPENDENCY IMPORTS ---
require('dotenv').config();
const axios = require('axios');
const fastq = require('fastq');
// =============================================================================
// == COMPONENT UPGRADE: Menggunakan modul 'js-levenshtein' yang lebih andal ==
const levenshtein = require('js-levenshtein');
// =============================================================================
const { TwitterApi } = require('twitter-api-v2');

// --- PHASE 2: MISSION CONFIGURATION ---

const POPULAR_PACKAGES = [
    'react', 'express', 'lodash', 'moment', 'chalk', 'axios', 'async',
    'webpack', 'next', 'vue', 'angular', 'jquery', 'bootstrap', 'tailwind',
    'eslint', 'prettier', 'jest', 'mocha', 'chai', 'jsonwebtoken',
    'dotenv', 'cors', 'body-parser', 'mongoose', 'sequelize', 'vite', 'prisma',
    'typescript', 'zod', 'next-auth', 'react-router-dom', 'redux'
];
const TYPO_THRESHOLD = 1;

// --- PHASE 3: WEAPON SYSTEMS INITIALIZATION ---

const twitterClient = new TwitterApi({
    appKey: process.env.TWITTER_API_KEY,
    appSecret: process.env.TWITTER_API_SECRET,
    accessToken: process.env.TWITTER_ACCESS_TOKEN,
    accessSecret: process.env.TWITTER_ACCESS_TOKEN_SECRET,
});

// --- PHASE 4: CORE LOGIC FUNCTIONS ---

async function postToTwitter(message) {
    try {
        await twitterClient.v2.tweet(message);
        console.log(`[>>>] ALERT BROADCASTED TO TWITTER SUCCESSFULLY.`);
    } catch (error) {
        console.error('[!!!] FAILED TO BROADCAST ALERT TO TWITTER:', error.message || error);
    }
}

async function analyzePackage(change) {
    if (change.doc && change.doc.name) {
        const packageName = change.doc.name;

        for (const popular of POPULAR_PACKAGES) {
            const distance = levenshtein(packageName, popular);
            if (distance > 0 && distance <= TYPO_THRESHOLD) {
                const alertMessage = `⚠️ Vektor Sentinel Alert ⚠️

Potential Typosquatting Attack Detected:
- Package: \`${packageName}\`
- Impersonating: \`${popular}\`
- Confidence Level: HIGH (Distance: ${distance})

#CyberSecurity #NPM #SupplyChainAttack #OpenSource #InfoSec`;
                
                console.warn(`[!!!] TARGET LOCKED: ${packageName} (Impersonating: ${popular})`);
                await postToTwitter(alertMessage);
                break;
            }
        }
    }
}

// --- PHASE 5: ENGINE & QUEUE SETUP ---

const analysisQueue = fastq.promise(analyzePackage, 1);
const processedPackages = new Set();

async function pollingEngine() {
    console.log(`[POLL ${new Date().toISOString()}] Fetching new packages...`);
    try {
        const response = await axios.get('https://registry.npmjs.org/-/v1/search?text=boost-exact:false&size=25&quality=0&popularity=0&maintenance=0');
        const packages = response.data.objects;

        for (const pkg of packages) {
            const packageName = pkg.package.name;
            if (!processedPackages.has(packageName)) {
                console.log(`[+] New package found via polling: ${packageName}`);
                processedPackages.add(packageName);
                
                const fakeChange = { doc: { name: packageName } };
                analysisQueue.push(fakeChange).catch(err => console.error('Analysis error:', err));
            }
        }
    } catch (error) {
        console.error('[!!!] Polling failed:', error.message);
    }
}

// --- PHASE 6: MISSION START ---

function startMission() {
    console.log('[*] Vektor Sentinel v0.4.3 activated. Polling Engine is LIVE.');
    console.log('[*] OPSEC Check: Ensure your .env file is loaded and correct.');
    
    pollingEngine();
    setInterval(pollingEngine, 30000); 
}

startMission();