// API Configuration
const API_URL = 'https://kshitijk20-nss.hf.space';

// Whitelisted domains - trusted sites that won't be checked
const WHITELISTED_DOMAINS = [
  // Google Services
  'google.com', 'gmail.com', 'youtube.com', 'drive.google.com', 'docs.google.com',
  'maps.google.com', 'meet.google.com', 'calendar.google.com', 'photos.google.com',
  
  // Microsoft
  'microsoft.com', 'outlook.com', 'office.com', 'live.com', 'hotmail.com',
  'onedrive.live.com', 'teams.microsoft.com', 'bing.com', 'msn.com', 'xbox.com',
  
  // Social Media
  'facebook.com', 'twitter.com', 'x.com', 'instagram.com', 'linkedin.com',
  'reddit.com', 'pinterest.com', 'tiktok.com', 'snapchat.com', 'whatsapp.com',
  
  // Developer Platforms
  'github.com', 'gitlab.com', 'bitbucket.org', 'stackoverflow.com', 'stackexchange.com',
  'npmjs.com', 'pypi.org', 'docker.com', 'jenkins.io', 'travis-ci.org',
  
  // Cloud & Productivity
  'notion.so', 'slack.com', 'zoom.us', 'dropbox.com', 'box.com', 'trello.com',
  'asana.com', 'monday.com', 'atlassian.net', 'jira.com', 'confluence.com',
  
  // E-commerce
  'amazon.com', 'ebay.com', 'walmart.com', 'target.com', 'bestbuy.com',
  'shopify.com', 'etsy.com', 'alibaba.com', 'aliexpress.com',
  
  // Streaming & Entertainment
  'netflix.com', 'hulu.com', 'spotify.com', 'twitch.tv', 'vimeo.com',
  'disneyplus.com', 'primevideo.com', 'crunchyroll.com',
  
  // Cloud Providers
  'aws.amazon.com', 'console.aws.amazon.com', 'azure.microsoft.com', 'cloud.google.com',
  'heroku.com', 'digitalocean.com', 'linode.com', 'vercel.com', 'netlify.com',
  'cloudflare.com', 'railway.app', 'render.com',
  
  // Finance & Banking
  'paypal.com', 'stripe.com', 'square.com', 'venmo.com', 'chase.com',
  'bankofamerica.com', 'wellsfargo.com', 'citibank.com', 'coinbase.com',
  
  // Education
  'coursera.org', 'udemy.com', 'edx.org', 'khanacademy.org', 'codecademy.com',
  'udacity.com', 'pluralsight.com', 'linkedin.com/learning',
  
  // News & Media
  'nytimes.com', 'bbc.com', 'cnn.com', 'reuters.com', 'theguardian.com',
  'bloomberg.com', 'forbes.com', 'medium.com', 'substack.com',
  
  // Design & Creative
  'figma.com', 'canva.com', 'adobe.com', 'behance.net', 'dribbble.com',
  
  // Communication
  'discord.com', 'telegram.org', 'signal.org', 'skype.com',
  
  // Other Major Services
  'wikipedia.org', 'archive.org', 'imdb.com', 'yelp.com', 'craigslist.org',
  'wordpress.com', 'blogger.com', 'tumblr.com', 'quora.com',
  
  // ML & AI Platforms
  'openai.com', 'huggingface.co', 'kaggle.com', 'colab.research.google.com',
  'paperswithcode.com', 'arxiv.org'
];

// Check if domain is whitelisted
function isWhitelisted(url) {
  try {
    const urlObj = new URL(url);
    const hostname = urlObj.hostname.toLowerCase();
    
    return WHITELISTED_DOMAINS.some(domain => {
      return hostname === domain || hostname.endsWith('.' + domain);
    });
  } catch (e) {
    return false;
  }
}

// Load statistics
function loadStats() {
  chrome.storage.local.get(['sitesChecked', 'threatsBlocked'], (result) => {
    document.getElementById('sites-checked').textContent = result.sitesChecked || 0;
    document.getElementById('threats-blocked').textContent = result.threatsBlocked || 0;
  });
}

// Extract URL features (enhanced version) - MUST match training data order!
async function extractFeatures(url, pageFeatures = null) {
  // CRITICAL: Maintain exact order as training data CSV
  const features = {};
  
  try {
    const urlObj = new URL(url);
    
    // 1. having_IP_Address
    features.having_IP_Address = /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/.test(urlObj.hostname) ? 1 : -1;
    
    // 2. URL_Length
    features.URL_Length = url.length < 54 ? -1 : (url.length <= 75 ? 0 : 1);
    
    // 3. Shortining_Service
    const shorteners = ['bit.ly', 'goo.gl', 'tinyurl', 't.co', 'ow.ly', 'buff.ly', 'adf.ly'];
    features.Shortining_Service = shorteners.some(s => urlObj.hostname.includes(s)) ? 1 : -1;
    
    // 4. having_At_Symbol
    features.having_At_Symbol = url.includes('@') ? 1 : -1;
    
    // 5. double_slash_redirecting
    const pathSlashes = urlObj.pathname.split('//').length - 1;
    features.double_slash_redirecting = pathSlashes > 0 ? 1 : -1;
    
    // 6. Prefix_Suffix
    features.Prefix_Suffix = urlObj.hostname.includes('-') ? 1 : -1;
    
    // 7. having_Sub_Domain
    const parts = urlObj.hostname.split('.');
    const dots = parts.length - 2;
    features.having_Sub_Domain = dots === 0 ? -1 : (dots === 1 ? 0 : 1);
    
    // 8. SSLfinal_State
    const hasHttps = urlObj.protocol === 'https:';
    const hasSuspiciousCert = urlObj.hostname.includes('http') || urlObj.hostname.includes('www-');
    features.SSLfinal_State = hasHttps && !hasSuspiciousCert ? -1 : (hasHttps ? 0 : 1);
    
    // 9. Domain_registeration_length
    features.Domain_registeration_length = -1;
    
    // 10. Favicon
    features.Favicon = pageFeatures?.Favicon ?? -1;
    
    // 11. port
    features.port = urlObj.port && urlObj.port !== '80' && urlObj.port !== '443' ? 1 : -1;
    
    // 12. HTTPS_token
    features.HTTPS_token = urlObj.hostname.toLowerCase().includes('https') ? 1 : -1;
    
    // 13. Request_URL
    features.Request_URL = pageFeatures?.Request_URL ?? -1;
    
    // 14. URL_of_Anchor
    features.URL_of_Anchor = pageFeatures?.URL_of_Anchor ?? -1;
    
    // 15. Links_in_tags
    features.Links_in_tags = pageFeatures?.Links_in_tags ?? -1;
    
    // 16. SFH
    features.SFH = pageFeatures?.SFH ?? -1;
    
    // 17. Submitting_to_email
    features.Submitting_to_email = pageFeatures?.Submitting_to_email ?? -1;
    
    // 18. Abnormal_URL
    features.Abnormal_URL = -1;
    
    // 19. Redirect
    features.Redirect = pageFeatures?.Redirect ?? -1;
    
    // 20. on_mouseover
    features.on_mouseover = pageFeatures?.on_mouseover ?? -1;
    
    // 21. RightClick
    features.RightClick = pageFeatures?.RightClick ?? -1;
    
    // 22. popUpWidnow
    features.popUpWidnow = pageFeatures?.popUpWidnow ?? -1;
    
    // 23. Iframe
    features.Iframe = pageFeatures?.Iframe ?? -1;
    
    // 24. age_of_domain
    features.age_of_domain = -1;
    
    // 25. DNSRecord
    features.DNSRecord = -1;
    
    // 26. web_traffic
    features.web_traffic = -1;
    
    // 27. Page_Rank
    features.Page_Rank = -1;
    
    // 28. Google_Index
    features.Google_Index = -1;
    
    // 29. Links_pointing_to_page
    features.Links_pointing_to_page = -1;
    
    // 30. Statistical_report
    features.Statistical_report = -1;
    
    return features;
  } catch (e) {
    console.error('Error extracting features:', e);
    return null;
  }
}

// Check URL with API
async function checkURL(url, pageFeatures = null) {
  try {
    // Check whitelist first
    if (isWhitelisted(url)) {
      return {
        isPhishing: false,
        confidence: 'High',
        whitelisted: true
      };
    }
    
    const features = await extractFeatures(url, pageFeatures);
    if (!features) {
      throw new Error('Invalid URL');
    }
    
    // Create proper CSV with headers
    const headers = Object.keys(features).join(',');
    const values = Object.values(features).join(',');
    const csvContent = `${headers}\n${values}`;
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const formData = new FormData();
    formData.append('file', blob, 'check.csv');
    
    const response = await fetch(`${API_URL}/predict`, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      throw new Error('API request failed');
    }
    
    // Parse response (API returns HTML table, we need to extract prediction)
    const html = await response.text();
    const isPhishing = html.includes('predicted_column') && html.includes('>1<'); // Check if prediction is 1
    
    return {
      isPhishing: isPhishing,
      confidence: isPhishing ? 'High' : 'Low'
    };
  } catch (error) {
    console.error('Error checking URL:', error);
    throw error;
  }
}

// Display result
function displayResult(container, result, url) {
  container.innerHTML = '';
  
  if (result.isPhishing) {
    container.innerHTML = `
      <div class="status danger">
        ⚠️ DANGER: Phishing Detected!
      </div>
    `;
    
    // Update stats
    chrome.storage.local.get(['threatsBlocked'], (data) => {
      const count = (data.threatsBlocked || 0) + 1;
      chrome.storage.local.set({ threatsBlocked: count });
      loadStats();
    });
  } else {
    const badge = result.whitelisted ? '🛡️' : '✅';
    const message = result.whitelisted ? 'Trusted Site' : 'Safe: No Threats Detected';
    container.innerHTML = `
      <div class="status safe">
        ${badge} ${message}
      </div>
    `;
  }
  
  // Update sites checked
  chrome.storage.local.get(['sitesChecked'], (data) => {
    const count = (data.sitesChecked || 0) + 1;
    chrome.storage.local.set({ sitesChecked: count });
    loadStats();
  });
}

// Check current tab
async function checkCurrentTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const url = tab.url;
  
  document.getElementById('current-url').textContent = url;
  
  // Skip chrome:// and extension pages
  if (url.startsWith('chrome://') || url.startsWith('chrome-extension://')) {
    document.getElementById('status-container').innerHTML = 
      '<div class="status checking">Cannot check browser internal pages</div>';
    return;
  }
  
  try {
    // Get page features from content script
    let pageFeatures = null;
    try {
      const response = await chrome.tabs.sendMessage(tab.id, { action: 'getPageFeatures' });
      pageFeatures = response?.features;
      console.log('Page features extracted:', pageFeatures);
    } catch (e) {
      console.log('Could not extract page features, using URL-only analysis');
    }
    
    const result = await checkURL(url, pageFeatures);
    displayResult(document.getElementById('status-container'), result, url);
  } catch (error) {
    document.getElementById('status-container').innerHTML = 
      '<div class="error">Error checking URL. Please try again.</div>';
  }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  loadStats();
  checkCurrentTab();
  
  // Manual URL check
  document.getElementById('check-btn').addEventListener('click', async () => {
    const url = document.getElementById('url-input').value.trim();
    const resultDiv = document.getElementById('manual-result');
    
    if (!url) {
      resultDiv.innerHTML = '<div class="error">Please enter a URL</div>';
      resultDiv.classList.add('show');
      return;
    }
    
    // Add protocol if missing
    const fullUrl = url.startsWith('http') ? url : `https://${url}`;
    
    resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div><span>Analyzing...</span></div>';
    resultDiv.classList.add('show');
    
    try {
      const result = await checkURL(fullUrl);
      displayResult(resultDiv, result, fullUrl);
    } catch (error) {
      resultDiv.innerHTML = '<div class="error">Error checking URL. Please try again.</div>';
    }
  });
});
