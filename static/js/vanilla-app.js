/**
 * NeuroVaidya - Total Vanilla Engine
 * High-performance interaction layer
 */

class NeuroUI {
    constructor() {
        this.navbar = document.getElementById('navbar');
        this.revealElements = document.querySelectorAll('.reveal');
        this.heroGlow = null;
        this.init();
    }

    init() {
        this.setupNeuralGlow();
        this.setupScrollEffects();
        this.setupIntersectionObserver();
        this.setupInteractiveElements();
        this.setupHeroAnimation();
        console.log('🧠 Neuro UI Engine Active');
    }

    /**
     * Creates a high-end neural mouse follower effect
     */
    setupNeuralGlow() {
        const glow = document.createElement('div');
        glow.className = 'hero-glow';
        document.body.appendChild(glow);
        this.heroGlow = glow;

        document.addEventListener('mousemove', (e) => {
            const { clientX, clientY } = e;
            // Smoothly move the glow with a slight lag
            requestAnimationFrame(() => {
                this.heroGlow.style.left = `${clientX - 300}px`;
                this.heroGlow.style.top = `${clientY - 300}px`;
            });
        });
    }

    setupScrollEffects() {
        window.addEventListener('scroll', () => {
            const scrolled = window.scrollY > 50;
            if (this.navbar) {
                if (scrolled) {
                    this.navbar.classList.add('scrolled');
                } else {
                    this.navbar.classList.remove('scrolled');
                }
            }
        }, { passive: true });
    }

    setupIntersectionObserver() {
        const observerOptions = {
            threshold: 0.15,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('active');
                    // Once revealed, we don't need to observe it anymore
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        this.revealElements.forEach(el => observer.observe(el));
    }

    setupInteractiveElements() {
        // Tilt effect for cards
        const cards = document.querySelectorAll('.glass-card, .product-card');
        cards.forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                
                const rotateX = (y - centerY) / 25;
                const rotateY = (centerX - x) / 25;
                
                card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-8px)`;
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
            });
        });

        // Smooth scroll for all anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                const targetId = anchor.getAttribute('href');
                if (targetId === '#') return;
                
                const target = document.querySelector(targetId);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    /**
     * Simple utility for managing modals with animations
     */
    static toggleModal(modalId, show = true) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        const card = modal.querySelector('.glass-card');

        if (show) {
            modal.style.display = 'flex';
            // Trigger reflow
            modal.offsetHeight;
            modal.style.opacity = '1';
            if (card) card.style.transform = 'scale(1)';
            document.body.style.overflow = 'hidden';
        } else {
            modal.style.opacity = '0';
            if (card) card.style.transform = 'scale(0.9)';
            setTimeout(() => {
                modal.style.display = 'none';
                document.body.style.overflow = '';
            }, 400);
        }
    }

    /**
     * Stunning Vanilla Canvas Animation
     */
    setupHeroAnimation() {
        const container = document.getElementById('neural-animation-root');
        if (!container) return;

        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        container.appendChild(canvas);

        let width, height, particles = [];

        const resize = () => {
            width = canvas.width = container.offsetWidth;
            height = canvas.height = container.offsetHeight;
        };

        window.addEventListener('resize', resize);
        resize();

        class Particle {
            constructor() {
                this.x = Math.random() * width;
                this.y = Math.random() * height;
                this.vx = (Math.random() - 0.5) * 0.5;
                this.vy = (Math.random() - 0.5) * 0.5;
                this.radius = Math.random() * 2;
            }

            update() {
                this.x += this.vx;
                this.y += this.vy;
                if (this.x < 0 || this.x > width) this.vx *= -1;
                if (this.y < 0 || this.y > height) this.vy *= -1;
            }

            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(0, 206, 209, 0.5)';
                ctx.fill();
            }
        }

        for (let i = 0; i < 60; i++) particles.push(new Particle());

        const animate = () => {
            ctx.clearRect(0, 0, width, height);
            
            particles.forEach((p, i) => {
                p.update();
                p.draw();
                
                for (let j = i + 1; j < particles.length; j++) {
                    const p2 = particles[j];
                    const dist = Math.hypot(p.x - p2.x, p.y - p2.y);
                    if (dist < 120) {
                        ctx.beginPath();
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.strokeStyle = `rgba(0, 206, 209, ${1 - dist / 120})`;
                        ctx.lineWidth = 0.5;
                        ctx.stroke();
                    }
                }
            });
            requestAnimationFrame(animate);
        };

        animate();
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    window.neuroUI = new NeuroUI();
});
