/**
 * Custom window resize handles for frameless pywebview windows.
 * Adds invisible drag zones along all edges and corners.
 */
(function() {
    const EDGE = 6;
    const handles = [
        { cls: 'rz-top',    style: `top:0;left:${EDGE}px;right:${EDGE}px;height:${EDGE}px;cursor:n-resize` },
        { cls: 'rz-bottom', style: `bottom:0;left:${EDGE}px;right:${EDGE}px;height:${EDGE}px;cursor:s-resize` },
        { cls: 'rz-left',   style: `left:0;top:${EDGE}px;bottom:${EDGE}px;width:${EDGE}px;cursor:w-resize` },
        { cls: 'rz-right',  style: `right:0;top:${EDGE}px;bottom:${EDGE}px;width:${EDGE}px;cursor:e-resize` },
        { cls: 'rz-tl',     style: `top:0;left:0;width:${EDGE}px;height:${EDGE}px;cursor:nw-resize` },
        { cls: 'rz-tr',     style: `top:0;right:0;width:${EDGE}px;height:${EDGE}px;cursor:ne-resize` },
        { cls: 'rz-bl',     style: `bottom:0;left:0;width:${EDGE}px;height:${EDGE}px;cursor:sw-resize` },
        { cls: 'rz-br',     style: `bottom:0;right:0;width:${EDGE}px;height:${EDGE}px;cursor:se-resize` },
    ];

    handles.forEach(h => {
        const el = document.createElement('div');
        el.className = h.cls;
        el.setAttribute('style', `position:fixed;${h.style};z-index:9999;-webkit-app-region:no-drag;`);
        document.body.appendChild(el);
    });

    let dragging = null;
    let startX, startY, startW, startH, startLeft, startTop;

    function getEdge(el) {
        const c = el.className;
        if (c.includes('-tl')) return 'tl';
        if (c.includes('-tr')) return 'tr';
        if (c.includes('-bl')) return 'bl';
        if (c.includes('-br')) return 'br';
        if (c.includes('-top')) return 't';
        if (c.includes('-bottom')) return 'b';
        if (c.includes('-left')) return 'l';
        if (c.includes('-right')) return 'r';
        return null;
    }

    document.addEventListener('mousedown', function(e) {
        const edge = getEdge(e.target);
        if (!edge) return;
        e.preventDefault();
        dragging = edge;
        startX = e.screenX;
        startY = e.screenY;
        startW = window.outerWidth;
        startH = window.outerHeight;
        startLeft = window.screenX;
        startTop = window.screenY;
    });

    document.addEventListener('mousemove', function(e) {
        if (!dragging) return;
        e.preventDefault();
        const dx = e.screenX - startX;
        const dy = e.screenY - startY;

        // Use pywebview API to resize
        if (window.pywebview && window.pywebview.api && window.pywebview.api.resize_window) {
            window.pywebview.api.resize_window(dragging, dx, dy, startW, startH, startLeft, startTop);
        }
    });

    document.addEventListener('mouseup', function() {
        dragging = null;
    });
})();
