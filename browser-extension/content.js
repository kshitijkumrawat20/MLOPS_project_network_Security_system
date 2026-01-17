// Content script - Runs on every page
console.log('Phishing Detector: Content script loaded');

// Extract page-level features from DOM
function extractPageFeatures() {
  const features = {};
  
  try {
    // Favicon analysis
    const favicon = document.querySelector('link[rel*="icon"]');
    const currentDomain = window.location.hostname;
    if (favicon) {
      const faviconUrl = new URL(favicon.href, window.location.href);
      features.Favicon = faviconUrl.hostname !== currentDomain ? 1 : -1;
    } else {
      features.Favicon = 1; // No favicon is suspicious
    }
    
    // Request_URL - Check if objects loaded from different domain
    const images = document.querySelectorAll('img, video, audio');
    let externalResources = 0;
    images.forEach(img => {
      try {
        const imgUrl = new URL(img.src, window.location.href);
        if (imgUrl.hostname !== currentDomain) externalResources++;
      } catch (e) {}
    });
    const externalRatio = images.length > 0 ? externalResources / images.length : 0;
    features.Request_URL = externalRatio > 0.22 ? 1 : (externalRatio > 0.61 ? 0 : -1);
    
    // URL_of_Anchor - Check anchor tags
    const anchors = document.querySelectorAll('a');
    let suspiciousAnchors = 0;
    anchors.forEach(a => {
      const href = a.getAttribute('href');
      if (!href || href === '#' || href.startsWith('javascript:')) {
        suspiciousAnchors++;
      } else {
        try {
          const anchorUrl = new URL(href, window.location.href);
          if (anchorUrl.hostname !== currentDomain) suspiciousAnchors++;
        } catch (e) {}
      }
    });
    const anchorRatio = anchors.length > 0 ? suspiciousAnchors / anchors.length : 0;
    features.URL_of_Anchor = anchorRatio > 0.31 ? 1 : (anchorRatio > 0.67 ? 0 : -1);
    
    // Links_in_tags - Check meta, script, link tags
    const metaLinks = document.querySelectorAll('meta, script[src], link[href]');
    let externalMetaLinks = 0;
    metaLinks.forEach(tag => {
      const src = tag.getAttribute('src') || tag.getAttribute('href') || tag.content;
      if (src) {
        try {
          const url = new URL(src, window.location.href);
          if (url.hostname !== currentDomain) externalMetaLinks++;
        } catch (e) {}
      }
    });
    const metaRatio = metaLinks.length > 0 ? externalMetaLinks / metaLinks.length : 0;
    features.Links_in_tags = metaRatio > 0.17 ? 1 : (metaRatio > 0.81 ? 0 : -1);
    
    // SFH - Server Form Handler
    const forms = document.querySelectorAll('form');
    let suspiciousForms = 0;
    forms.forEach(form => {
      const action = form.getAttribute('action');
      if (!action || action === '' || action === 'about:blank') {
        suspiciousForms++;
      } else {
        try {
          const formUrl = new URL(action, window.location.href);
          if (formUrl.hostname !== currentDomain) suspiciousForms++;
        } catch (e) {
          suspiciousForms++;
        }
      }
    });
    features.SFH = forms.length > 0 && suspiciousForms > 0 ? 1 : -1;
    
    // Submitting_to_email - Check if form submits to email
    let hasEmailSubmit = false;
    forms.forEach(form => {
      const action = form.getAttribute('action');
      if (action && action.startsWith('mailto:')) hasEmailSubmit = true;
    });
    features.Submitting_to_email = hasEmailSubmit ? 1 : -1;
    
    // Redirect - Count meta redirects
    const metaRefresh = document.querySelector('meta[http-equiv="refresh"]');
    features.Redirect = metaRefresh ? 1 : -1;
    
    // on_mouseover - Check for mouseover events that change status bar
    let hasMouseoverStatusChange = false;
    anchors.forEach(a => {
      const mouseover = a.getAttribute('onmouseover') || a.getAttribute('onmouseout');
      if (mouseover && (mouseover.includes('window.status') || mouseover.includes('location'))) {
        hasMouseoverStatusChange = true;
      }
    });
    features.on_mouseover = hasMouseoverStatusChange ? 1 : -1;
    
    // RightClick - Check if right-click is disabled
    const hasRightClickDisable = document.body.getAttribute('oncontextmenu') === 'return false' ||
                                  document.oncontextmenu === null;
    features.RightClick = hasRightClickDisable ? 1 : -1;
    
    // popUpWidnow - Check for popup windows
    const scripts = document.querySelectorAll('script');
    let hasPopup = false;
    scripts.forEach(script => {
      if (script.textContent.includes('window.open') || 
          script.textContent.includes('popup')) {
        hasPopup = true;
      }
    });
    features.popUpWidnow = hasPopup ? 1 : -1;
    
    // Iframe - Check for iframes
    const iframes = document.querySelectorAll('iframe');
    features.Iframe = iframes.length > 0 ? 1 : -1;
    
    return features;
  } catch (error) {
    console.error('Error extracting page features:', error);
    return null;
  }
}

// Listen for messages from popup or background
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getCurrentURL') {
    sendResponse({ url: window.location.href });
  }
  
  if (request.action === 'getPageFeatures') {
    const features = extractPageFeatures();
    sendResponse({ features: features });
  }
  
  if (request.action === 'showWarning') {
    showPhishingWarning();
  }
  
  return true;
});

// Show warning banner on page
function showPhishingWarning() {
  // Check if warning already exists
  if (document.getElementById('phishing-warning-banner')) {
    return;
  }
  
  const banner = document.createElement('div');
  banner.id = 'phishing-warning-banner';
  banner.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: linear-gradient(135deg, #ff6b6b 0%, #c92a2a 100%);
    color: white;
    padding: 15px;
    text-align: center;
    font-family: Arial, sans-serif;
    font-size: 16px;
    font-weight: bold;
    z-index: 999999;
    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    animation: slideDown 0.5s ease;
  `;
  
  banner.innerHTML = `
    <div style="max-width: 1200px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between;">
      <div style="flex: 1;">
        ⚠️ <strong>WARNING:</strong> This site has been identified as potentially dangerous!
      </div>
      <button id="close-warning" style="
        background: rgba(255,255,255,0.2);
        border: 2px solid white;
        color: white;
        padding: 8px 20px;
        border-radius: 5px;
        cursor: pointer;
        font-weight: bold;
        margin-left: 20px;
      ">
        Dismiss
      </button>
    </div>
  `;
  
  // Add animation
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideDown {
      from {
        transform: translateY(-100%);
      }
      to {
        transform: translateY(0);
      }
    }
  `;
  document.head.appendChild(style);
  
  document.body.insertBefore(banner, document.body.firstChild);
  
  // Close button
  document.getElementById('close-warning').addEventListener('click', () => {
    banner.remove();
  });
  
  // Blur page content
  document.body.style.filter = 'blur(2px)';
  
  // Remove blur when warning is dismissed
  const observer = new MutationObserver(() => {
    if (!document.getElementById('phishing-warning-banner')) {
      document.body.style.filter = '';
      observer.disconnect();
    }
  });
  
  observer.observe(document.body, { childList: true });
}

// Auto-check on page load (optional - can be enabled in settings)
// Uncomment to enable automatic checking
/*
window.addEventListener('load', () => {
  chrome.runtime.sendMessage({ 
    action: 'checkPage', 
    url: window.location.href 
  });
});
*/
