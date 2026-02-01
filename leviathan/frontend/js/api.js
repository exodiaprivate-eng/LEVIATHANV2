/**
 * Python Bridge - Communication with PyWebView backend
 */

async function callPython(method, ...args) {
    try {
        if (!window.pywebview || !window.pywebview.api) {
            console.warn('PyWebView API not available yet');
            return null;
        }
        const result = await window.pywebview.api[method](...args);
        return typeof result === 'string' ? JSON.parse(result) : result;
    } catch (error) {
        console.error(`Error calling ${method}:`, error);
        return null;
    }
}
