/* Great Scale atlas runtime — drag, scrub, view presets */
(function () {
  const VIEW_PRESETS = { Watch: { az: 35, el: 25 }, Observer: { az: 0, el: 80 }, Forward: { az: 90, el: 15 }, Adjacent: { az: -40, el: 20 }, Down: { az: 0, el: -55 } };
  let camAz = 35, camEl = 25, camDist = 1, scrubMode = false;
  function project3(x, y, z, W, H) {
    const az = (camAz * Math.PI) / 180, el = (camEl * Math.PI) / 180;
    let x1 = x * Math.cos(az) - z * Math.sin(az);
    let z1 = x * Math.sin(az) + z * Math.cos(az);
    let y1 = y * Math.cos(el) - z1 * Math.sin(el);
    let z2 = y * Math.sin(el) + z1 * Math.cos(el);
    const f = (320 * camDist) / (2.5 + z2);
    return [W * 0.42 + x1 * f, H * 0.48 - y1 * f];
  }
  const canvas = document.getElementById('cv') || document.getElementById('c');
  let dragging = false, lx = 0, ly = 0;
  if (canvas) {
    canvas.addEventListener('pointerdown', (e) => { dragging = true; lx = e.clientX; ly = e.clientY; canvas.setPointerCapture?.(e.pointerId); });
    window.addEventListener('pointerup', () => { dragging = false; });
    window.addEventListener('pointermove', (e) => {
      if (!dragging) return;
      camAz += (e.clientX - lx) * 0.4;
      camEl = Math.max(-89, Math.min(89, camEl - (e.clientY - ly) * 0.3));
      lx = e.clientX; ly = e.clientY;
    });
    canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      camDist = Math.max(0.35, Math.min(3.5, camDist * (e.deltaY > 0 ? 0.92 : 1.08)));
    }, { passive: false });
  }
  window.GreatScaleAtlas = {
    camAz: () => camAz, camEl: () => camEl, camDist: () => camDist,
    project3, VIEW_PRESETS, version: '0.4.2',
    setView: (v) => { const p = VIEW_PRESETS[v]; if (p) { camAz = p.az; camEl = p.el; } },
  };
  console.log('Great Scale atlas 0.4.2 ready');
})();
