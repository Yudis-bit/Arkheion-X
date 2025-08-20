// =============================================================================
// == VEKTOR SENTINEL v0.6.0
// == INTERNATIONAL STANDARD // ACTIONS-READY STATELESS ENGINE
// == AUTHOR: ARKHEION-X HYPEROPS
// =============================================================================

// --- PHASE 1: DEPENDENCY IMPORTS ---
require('dotenv').config();
const axios = require('axios');
const fastq = require('fastq');
const levenshtein = require('js-levenshtein');
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
                const alertMessage = `[VEKTOR SENTINEL // ALERT]

SIG-TYPE: Typosquatting
TARGET: \`${packageName}\`
MIMICS: \`${popular}\`
CONFIDENCE: HIGH (dist: ${distance})

#CyberSecurity #NPM #SupplyChainAttack #ARKHEIONX`;
                
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
                console.log(`[+] New package found: ${packageName}`);
                processedPackages.add(packageName);
                
                const fakeChange = { doc: { name: packageName } };
                analysisQueue.push(fakeChange).catch(err => console.error('Analysis error:', err));
            }
        }
    } catch (error) {
        console.error('[!!!] Polling failed:', error.message);
    }
}

// --- MISSION EXECUTION ---
// Direct engine execution. No loops, no startMission.
// GitHub Actions (cron) will serve as the loop.
console.log('[*] ARKHEION-X Agent activated. Executing mission...');
pollingEngine();