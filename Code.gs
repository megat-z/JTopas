// -------- Script Properties Helper --------
function getConfig() { return PropertiesService.getScriptProperties().getProperty("GITHUB_PAT"); }

// -------- Sheets management --------
let _doc, _ss = {};
function getss(sheet) {
  const s = String(sheet);
  if (!_ss[s]) {
    if (!_doc) { _doc = SpreadsheetApp.getActiveSpreadsheet(); }
    _ss[s] = _doc.getSheetByName(s);
    if (!_ss[s]){
      const template = _doc.getSheetByName('log');
      _ss[s] = _doc.insertSheet(s, {template: template});
    }
  }
  return _ss[s];
}

// -------- File changes detection --------
function detectFile(update, path){
  return update.commits.some(commit => {
    const added = commit.added && commit.added.includes(path);
    const modified = commit.modified && commit.modified.includes(path);
    return added || modified;
  });
}

// -------- Trigger dispatch workflow --------
function triggerDispatches(url, event, branch) {
  const pat = getConfig();
  if (!pat ) return getss(branch).appendRow([new Date(), "FATAL: Missing GITHUB_PAT in script properties."]);
  try {
    const response = UrlFetchApp.fetch(url + '/dispatches', {
      method: 'post',
      contentType: 'application/json',
      headers: {
        'Authorization': 'Bearer ' + pat,
        'Accept': 'application/vnd.github.v3+json'
      },
      payload: JSON.stringify({
        event_type: event,
        client_payload: {
          triggered_by: 'Google Apps Script Webhook',
          timestamp: new Date().toISOString(),
          branch: branch
        }
      }),
      muteHttpExceptions: true
    });
    if (response.getResponseCode() === 204) return;
    throw new Error(`Trigger dispatch failed: ${response.getContentText()}`);
  } catch (e) {
    getss(branch).appendRow([new Date(), "FATAL: Error during triggerDispatches UrlFetchApp.fetch.", e.toString()]);
  }
}

// -------- Main webhook handler --------
function doPost(e) {
  const update = JSON.parse(e.postData.contents);
  try {
    if (!update.commits || update.commits.length === 0) {
      getss('log').appendRow([new Date(), "Received a webhook event without commits.", JSON.stringify(update, null, 2)]);
      return ContentService.createTextOutput("OK - Ping received").setMimeType(ContentService.MimeType.TEXT);
    }

    // -------- Branch detection --------
    const parts = update.ref.split('/');
    const branch = parts.length >= 3 ? parts.slice(2).join('/') : null;
    getss(branch).appendRow([new Date(), JSON.stringify(update, null, 2)]);

    // -------- Switch case for file changes --------
    let workflow, logMsg, resultMsg;
    
    switch (true) {
      case detectFile(update, 'dff.txt'):
        workflow = 'prompt-llm';
        logMsg = "Prompting LLM";
        resultMsg = "OK - Prompt LLM Triggered";
        break;
      case detectFile(update, 'llm.txt'):
        workflow = 'qi-pso';
        logMsg = "Prioritizing test cases";
        resultMsg = "OK - Quantum-Inspired Particle Swarm Optimization Triggered";
        break;
      default:
        workflow = 'git-diff';
        logMsg = "Extracting code changes";
        resultMsg = "OK - Git Diff Triggered";
        break;
    }

    triggerDispatches(update.repository.url, workflow, branch);
    getss(branch).appendRow([new Date(), logMsg, JSON.stringify(update, null, 2)]);
    return ContentService.createTextOutput(resultMsg).setMimeType(ContentService.MimeType.TEXT);

  } catch (error) {
    getss('log').appendRow([new Date(), "An error occurred.", JSON.stringify(update, null, 2), error.stack]);
    return ContentService.createTextOutput("Error").setMimeType(ContentService.MimeType.TEXT).setStatusCode(500);
  }
}