var e=class{constructor(e){this.root=document.getElementById(e),this.root&&(this.totalFrames=130,this.frameRate=20,this.frames=[],this.loadedCount=0,this.isStarted=!1,this.init())}init(){this.root.style.position=`absolute`,this.root.style.width=`100%`,this.root.style.height=`100%`,this.root.style.overflow=`hidden`,this.loadingWrap=document.createElement(`div`),this.loadingWrap.style.cssText=`
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      color: #d4af37;
      z-index: 10;
      text-align: center;
      font-family: 'Outfit', sans-serif;
    `,this.loadingWrap.innerHTML=`
      <div style="font-size: 24px; margin-bottom: 10px;">Neurolink Stabilizing...</div>
      <div id="hero-progress-text" style="font-size: 14px;">0%</div>
      <div style="width: 200px; height: 2px; background: rgba(212, 175, 55, 0.2); margin-top: 10px;">
        <div id="hero-progress-bar" style="width: 0%; height: 100%; background: #d4af37; transition: width 0.3s ease;"></div>
      </div>
    `,this.root.appendChild(this.loadingWrap),this.canvas=document.createElement(`canvas`),this.canvas.width=window.innerWidth,this.canvas.height=window.innerHeight,this.canvas.style.cssText=`
      display: none;
      width: 100%;
      height: 100%;
      object-fit: cover;
    `,this.root.appendChild(this.canvas),this.ctx=this.canvas.getContext(`2d`),this.preloadFrames(),window.addEventListener(`resize`,()=>{this.canvas.width=window.innerWidth,this.canvas.height=window.innerHeight})}preloadFrames(){for(let e=1;e<=this.totalFrames;e++){let t=new Image;t.src=`/static/images/frames/ezgif-frame-${String(e).padStart(3,`0`)}.jpg`,t.onload=()=>this.handleImageLoad(e,t),t.onerror=()=>console.error(`Failed to load frame ${e}`)}}handleImageLoad(e,t){this.frames[e-1]=t,this.loadedCount++;let n=Math.round(this.loadedCount/this.totalFrames*100),r=document.getElementById(`hero-progress-bar`),i=document.getElementById(`hero-progress-text`);r&&(r.style.width=`${n}%`),i&&(i.textContent=`${n}%`),this.loadedCount===this.totalFrames&&!this.isStarted&&this.startAnimation()}startAnimation(){this.isStarted=!0,this.loadingWrap.style.display=`none`,this.canvas.style.display=`block`;let e=0,t=0,n=1e3/this.frameRate,r=i=>{if(i-t>n){let n=this.frames[e];if(n&&n.complete){let{width:r,height:a}=this.canvas;this.ctx.clearRect(0,0,r,a);let o=Math.max(r/n.width,a/n.height),s=r/2-n.width/2*o,c=a/2-n.height/2*o;this.ctx.drawImage(n,s,c,n.width*o,n.height*o),e=(e+1)%this.totalFrames,t=i}}requestAnimationFrame(r)};requestAnimationFrame(r)}};document.addEventListener(`DOMContentLoaded`,()=>{new e(`hero-root`)});