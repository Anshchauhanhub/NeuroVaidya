/**
 * NEUROVAIDYA - Hero Animation Manager (Vanilla JS + Vite)
 * Flicker-free Canvas implementation with parallel preloading.
 */

class HeroManager {
  constructor(rootId) {
    this.root = document.getElementById(rootId)
    if (!this.root) return

    this.totalFrames = 130
    this.frameRate = 20
    this.frames = []
    this.loadedCount = 0
    this.isStarted = false

    this.init()
  }

  init() {
    // 1. Setup Wrapper and Loading UI
    this.root.style.position = 'absolute'
    this.root.style.width = '100%'
    this.root.style.height = '100%'
    this.root.style.overflow = 'hidden'

    this.loadingWrap = document.createElement('div')
    this.loadingWrap.style.cssText = `
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      color: #d4af37;
      z-index: 10;
      text-align: center;
      font-family: 'Outfit', sans-serif;
    `
    this.loadingWrap.innerHTML = `
      <div style="font-size: 24px; margin-bottom: 10px;">Neurolink Stabilizing...</div>
      <div id="hero-progress-text" style="font-size: 14px;">0%</div>
      <div style="width: 200px; height: 2px; background: rgba(212, 175, 55, 0.2); margin-top: 10px;">
        <div id="hero-progress-bar" style="width: 0%; height: 100%; background: #d4af37; transition: width 0.3s ease;"></div>
      </div>
    `
    this.root.appendChild(this.loadingWrap)

    // 2. Setup Canvas
    this.canvas = document.createElement('canvas')
    this.canvas.width = window.innerWidth
    this.canvas.height = window.innerHeight
    this.canvas.style.cssText = `
      display: none;
      width: 100%;
      height: 100%;
      object-fit: cover;
    `
    this.root.appendChild(this.canvas)
    this.ctx = this.canvas.getContext('2d')

    // 3. Preload Frames
    this.preloadFrames()

    // 4. Handle Resize
    window.addEventListener('resize', () => {
      this.canvas.width = window.innerWidth
      this.canvas.height = window.innerHeight
    })
  }

  preloadFrames() {
    for (let i = 1; i <= this.totalFrames; i++) {
      const img = new Image()
      const frameNum = String(i).padStart(3, '0')
      img.src = `/static/images/frames/ezgif-frame-${frameNum}.jpg`
      img.onload = () => this.handleImageLoad(i, img)
      img.onerror = () => console.error(`Failed to load frame ${i}`)
    }
  }

  handleImageLoad(index, img) {
    this.frames[index - 1] = img
    this.loadedCount++

    const progress = Math.round((this.loadedCount / this.totalFrames) * 100)
    const progressBar = document.getElementById('hero-progress-bar')
    const progressText = document.getElementById('hero-progress-text')

    if (progressBar) progressBar.style.width = `${progress}%`
    if (progressText) progressText.textContent = `${progress}%`

    if (this.loadedCount === this.totalFrames && !this.isStarted) {
      this.startAnimation()
    }
  }

  startAnimation() {
    this.isStarted = true
    this.loadingWrap.style.display = 'none'
    this.canvas.style.display = 'block'

    let currentFrame = 0
    let lastTime = 0
    const interval = 1000 / this.frameRate

    const animate = (time) => {
      const delta = time - lastTime

      if (delta > interval) {
        const img = this.frames[currentFrame]
        if (img && img.complete) {
          const { width, height } = this.canvas
          this.ctx.clearRect(0, 0, width, height)

          const scale = Math.max(width / img.width, height / img.height)
          const x = (width / 2) - (img.width / 2) * scale
          const y = (height / 2) - (img.height / 2) * scale

          this.ctx.drawImage(img, x, y, img.width * scale, img.height * scale)
          currentFrame = (currentFrame + 1) % this.totalFrames
          lastTime = time
        }
      }
      requestAnimationFrame(animate)
    }

    requestAnimationFrame(animate)
  }
}

// Auto-initialize when the script is loaded
document.addEventListener('DOMContentLoaded', () => {
  new HeroManager('hero-root')
})
